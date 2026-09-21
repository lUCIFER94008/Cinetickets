import re
from datetime import datetime, timezone
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc
from services.theatre_service import theatre_service

class ShowService:
    def get_shows(self, movie_id=None, theatre_id=None, date_str=None, city=None):
        db = get_db()
        filter_query = {}

        if movie_id:
            m_oid = to_object_id(movie_id)
            if m_oid:
                filter_query['movie_id'] = m_oid

        if theatre_id:
            t_oid = to_object_id(theatre_id)
            if t_oid:
                filter_query['theatre_id'] = t_oid
        elif city:
            # Filter by theatres located in this city
            city_theatres = theatre_service.get_theatres(city=city)
            city_t_ids = [to_object_id(t['id']) for t in city_theatres if to_object_id(t['id'])]
            if city_t_ids:
                filter_query['theatre_id'] = {'$in': city_t_ids}
            else:
                # No theatres in this city -> return empty shows list
                return []

        if date_str:
            filter_query['date'] = date_str

        shows = list(db.shows.find(filter_query).sort('time', 1))

        # Pre-fetch movies and theatres to prevent N+1 queries
        movie_ids = list({s.get('movie_id') for s in shows if s.get('movie_id')})
        theatre_ids = list({s.get('theatre_id') for s in shows if s.get('theatre_id')})

        movies_map = {m['_id']: serialize_doc(m) for m in db.movies.find({'_id': {'$in': movie_ids}})}
        theatres_map = {t['_id']: serialize_doc(t) for t in db.theatres.find({'_id': {'$in': theatre_ids}})}

        enriched = []
        for s in shows:
            s_serialized = serialize_doc(s)
            s_serialized['movie'] = movies_map.get(s.get('movie_id'))
            s_serialized['theatre'] = theatres_map.get(s.get('theatre_id'))
            enriched.append(s_serialized)

        # Additional safeguard: if city was passed, ensure enriched theatre is in target city
        if city:
            city_lower = str(city).strip().lower()
            enriched = [
                s for s in enriched 
                if s.get('theatre') and str(s['theatre'].get('city', '')).strip().lower() == city_lower
            ]

        return enriched

    def get_show_by_id(self, show_id):
        s_oid = to_object_id(show_id)
        if not s_oid:
            return None
        db = get_db()
        show = db.shows.find_one({'_id': s_oid})
        if not show:
            return None

        movie = db.movies.find_one({'_id': show.get('movie_id')})
        theatre = db.theatres.find_one({'_id': show.get('theatre_id')})

        s_serialized = serialize_doc(show)
        s_serialized['movie'] = serialize_doc(movie)
        s_serialized['theatre'] = serialize_doc(theatre)
        return s_serialized

    def find_or_create_show(self, movie_id, theatre_id, time_str, date_str=None, screen="Screen 1", show_format="2D", price=220):
        db = get_db()
        m_oid = to_object_id(movie_id)
        t_oid = to_object_id(theatre_id)

        if not m_oid or not t_oid:
            return None

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d")

        query = {
            'movie_id': m_oid,
            'theatre_id': t_oid,
            'time': time_str,
            'date': date_str
        }

        existing = db.shows.find_one(query)
        if existing:
            return self.get_show_by_id(existing['_id'])

        new_show = {
            'movie_id': m_oid,
            'theatre_id': t_oid,
            'screen': screen,
            'date': date_str,
            'time': time_str,
            'format': show_format,
            'price': float(price),
            'created_at': datetime.now(timezone.utc)
        }

        res = db.shows.insert_one(new_show)
        return self.get_show_by_id(res.inserted_id)

show_service = ShowService()

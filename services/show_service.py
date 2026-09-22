import re
from datetime import datetime, timedelta, timezone
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc
from services.theatre_service import theatre_service

class ShowService:
    def get_weekly_dates(self, start_date=None):
        if not start_date:
            base = datetime.now()
        else:
            try:
                base = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                base = datetime.now()

        dates = []
        for i in range(7):
            d = base + timedelta(days=i)
            dates.append({
                'date_str': d.strftime("%Y-%m-%d"),
                'day_name': d.strftime("%a").upper(),
                'day_num': d.strftime("%d"),
                'month_name': d.strftime("%b").upper(),
                'formatted': d.strftime("%a, %d %b"),
                'full_formatted': d.strftime("%A, %d %B %Y"),
                'is_today': i == 0
            })
        return dates

    def get_shows(self, movie_id=None, theatre_id=None, date_str=None, city=None, status=None, search=None):
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
            city_theatres = theatre_service.get_theatres(city=city)
            city_t_ids = [to_object_id(t['id']) for t in city_theatres if to_object_id(t['id'])]
            if city_t_ids:
                filter_query['theatre_id'] = {'$in': city_t_ids}
            else:
                return []

        if date_str:
            filter_query['date'] = date_str

        shows = list(db.shows.find(filter_query).sort('time', 1))
        if not shows:
            return []

        # Pre-fetch movies and theatres to prevent N+1 queries
        movie_ids = list({s.get('movie_id') for s in shows if s.get('movie_id')})
        theatre_ids = list({s.get('theatre_id') for s in shows if s.get('theatre_id')})
        show_ids = [s['_id'] for s in shows]

        movies_map = {m['_id']: serialize_doc(m) for m in db.movies.find({'_id': {'$in': movie_ids}})}
        theatres_map = {t['_id']: serialize_doc(t) for t in db.theatres.find({'_id': {'$in': theatre_ids}})}

        # Bulk seat counts query
        seat_agg = list(db.seats.aggregate([
            {'$match': {'show_id': {'$in': show_ids}, 'is_booked': True}},
            {'$group': {'_id': '$show_id', 'count': {'$sum': 1}}}
        ]))
        booked_counts_map = {item['_id']: item['count'] for item in seat_agg}

        enriched = []
        for s in shows:
            s_serialized = serialize_doc(s)
            s_serialized['movie'] = movies_map.get(s.get('movie_id'))
            s_serialized['theatre'] = theatres_map.get(s.get('theatre_id'))

            s_oid = s['_id']
            total_seats = int(s.get('total_seats', 120))
            booked_count = booked_counts_map.get(s_oid, 0)
            available_seats = s.get('available_seats', total_seats - booked_count)
            if available_seats < 0:
                available_seats = 0

            status = s.get('status')
            if not status or status == 'available':
                if available_seats == 0:
                    status = 'sold_out'
                elif available_seats <= 15:
                    status = 'filling_fast'
                else:
                    status = 'available'

            s_serialized['total_seats'] = total_seats
            s_serialized['available_seats'] = available_seats
            s_serialized['status'] = status
            s_serialized['start_time'] = s.get('start_time', s.get('time'))
            s_serialized['end_time'] = s.get('end_time', '')
            s_serialized['screen'] = s.get('screen', 'Screen 1')
            s_serialized['screen_id'] = s.get('screen_id', s.get('screen', 'Screen 1'))

            enriched.append(s_serialized)

        if city:
            city_lower = str(city).strip().lower()
            enriched = [
                s for s in enriched 
                if s.get('theatre') and str(s['theatre'].get('city', '')).strip().lower() == city_lower
            ]

        if status:
            st_lower = str(status).strip().lower()
            enriched = [s for s in enriched if str(s.get('status', '')).strip().lower() == st_lower]

        if search:
            q = str(search).strip().lower()
            enriched = [
                s for s in enriched
                if q in str(s.get('movie', {}).get('title', '')).lower()
                or q in str(s.get('theatre', {}).get('name', '')).lower()
                or q in str(s.get('screen', '')).lower()
                or q in str(s.get('date', '')).lower()
                or q in str(s.get('start_time', '')).lower()
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
        
        # Calculate seat availability
        total_seats = show.get('total_seats', 120)
        booked_count = db.seats.count_documents({'show_id': s_oid, 'is_booked': True})
        avail = show.get('available_seats', total_seats - booked_count)
        s_serialized['available_seats'] = max(0, avail)
        s_serialized['total_seats'] = total_seats
        s_serialized['start_time'] = show.get('start_time', show.get('time'))
        s_serialized['end_time'] = show.get('end_time', '')
        s_serialized['screen_id'] = show.get('screen_id', show.get('screen', 'Screen 1'))

        return s_serialized

    def find_or_create_show(self, movie_id, theatre_id, time_str, date_str=None, screen="Screen 1", show_format="2D", price=220, start_time=None, end_time=None, total_seats=120, status="available"):
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
            'screen_id': screen,
            'screen': screen,
            'date': date_str,
            'time': time_str,
            'start_time': start_time or time_str,
            'end_time': end_time or '',
            'format': show_format,
            'price': float(price),
            'available_seats': int(total_seats),
            'total_seats': int(total_seats),
            'status': status,
            'active': True,
            'created_at': datetime.now(timezone.utc)
        }

        res = db.shows.insert_one(new_show)
        return self.get_show_by_id(res.inserted_id)

show_service = ShowService()

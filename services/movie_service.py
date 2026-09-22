from datetime import datetime, timezone
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc
from utils.youtube_helpers import get_youtube_embed_url, extract_youtube_id

class MovieService:
    def _enrich_movie(self, movie):
        if not movie:
            return movie
        if isinstance(movie, list):
            return [self._enrich_movie(m) for m in movie]
        if isinstance(movie, dict):
            trailer = movie.get('trailer_url') or movie.get('trailer') or ''
            movie['trailer_url'] = trailer
            if trailer:
                movie['youtube_embed_url'] = get_youtube_embed_url(trailer)
                movie['youtube_id'] = extract_youtube_id(trailer)
            else:
                movie['youtube_embed_url'] = None
                movie['youtube_id'] = None
        return movie

    def get_movies(self, status=None, genre=None, search=None, sort_by=None):
        db = get_db()
        filter_query = {}

        if status:
            filter_query['status'] = status
        if genre:
            filter_query['genre'] = genre
        if search:
            filter_query['$or'] = [
                {'title': {'$regex': search, '$options': 'i'}},
                {'genre': {'$regex': search, '$options': 'i'}},
                {'language': {'$regex': search, '$options': 'i'}}
            ]

        cursor = db.movies.find(filter_query)

        if sort_by == 'rating':
            cursor = cursor.sort('rating', -1)
        elif sort_by == 'name':
            cursor = cursor.sort('title', 1)
        else:
            cursor = cursor.sort('release_date', -1)

        movies = list(cursor)
        return self._enrich_movie(serialize_doc(movies))

    def get_movie_by_id(self, movie_id):
        m_oid = to_object_id(movie_id)
        if not m_oid:
            return None
        db = get_db()
        movie = db.movies.find_one({'_id': m_oid})
        return self._enrich_movie(serialize_doc(movie))

    def create_movie(self, data):
        db = get_db()
        res = db.movies.insert_one(data)
        data['_id'] = res.inserted_id
        return self._enrich_movie(serialize_doc(data))

    def get_reviews(self, movie_id):
        m_oid = to_object_id(movie_id)
        db = get_db()
        query = {'$or': [{'movie_id': m_oid}, {'movie_id': str(movie_id)}]} if m_oid else {'movie_id': str(movie_id)}
        reviews = list(db.reviews.find(query).sort('created_at', -1))
        return serialize_doc(reviews)

    def get_review_stats(self, movie_id):
        reviews = self.get_reviews(movie_id)
        total = len(reviews)
        if total == 0:
            return {
                'total': 0,
                'avg_rating': 0.0,
                'counts': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0},
                'percentages': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
            }

        total_stars = sum(int(r.get('rating', 5)) for r in reviews)
        avg_rating = round(total_stars / total, 1)

        counts = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        for r in reviews:
            rate = int(r.get('rating', 5))
            if 1 <= rate <= 5:
                counts[rate] += 1

        percentages = {star: round((count / total) * 100) for star, count in counts.items()}
        return {
            'total': total,
            'avg_rating': avg_rating,
            'counts': counts,
            'percentages': percentages
        }

    def add_review(self, movie_id, user_id, user_name, rating, comment):
        db = get_db()
        m_oid = to_object_id(movie_id)
        if not m_oid:
            return False, "Invalid movie ID."

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return False, "Rating must be between 1 and 5 stars."
        except (ValueError, TypeError):
            return False, "Invalid rating format."

        comment = (comment or '').strip()
        if not comment:
            return False, "Review comment cannot be empty."

        # Check if user has a verified booking
        booking = db.bookings.find_one({
            'user_id': str(user_id),
            '$or': [{'movie_id': str(movie_id)}, {'movie_id': m_oid}],
            'booking_status': 'confirmed'
        })
        is_verified = bool(booking)

        review_doc = {
            'movie_id': m_oid,
            'user_id': str(user_id),
            'user_name': user_name or 'Anonymous User',
            'rating': rating,
            'comment': comment,
            'verified_booking': is_verified,
            'created_at': datetime.now(timezone.utc)
        }

        db.reviews.insert_one(review_doc)

        # Recalculate average rating for movie
        all_reviews = list(db.reviews.find({'movie_id': m_oid}))
        if all_reviews:
            new_avg = round(sum(r['rating'] for r in all_reviews) / len(all_reviews), 1)
            db.movies.update_one({'_id': m_oid}, {'$set': {'rating': new_avg}})

        return True, "Review submitted successfully!"

movie_service = MovieService()

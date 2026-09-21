from datetime import datetime, timezone, timedelta, date
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc

class AdminService:
    def get_dashboard_stats(self):
        db = get_db()
        today_str = datetime.now().strftime("%Y-%m-%d")

        total_users = db.users.count_documents({})
        total_movies = db.movies.count_documents({})
        total_theatres = db.theatres.count_documents({})
        total_shows = db.shows.count_documents({})
        total_bookings = db.bookings.count_documents({})
        today_bookings = db.bookings.count_documents({'date': today_str})

        revenue_agg = list(db.bookings.aggregate([
            {'$match': {'booking_status': 'confirmed'}},
            {'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}
        ]))
        total_revenue = revenue_agg[0]['total'] if revenue_agg else 0.0

        return {
            'total_users': total_users,
            'total_movies': total_movies,
            'total_theatres': total_theatres,
            'total_shows': total_shows,
            'total_bookings': total_bookings,
            'today_bookings': today_bookings,
            'total_revenue': round(total_revenue, 2)
        }

    # User Management
    def get_all_users(self):
        db = get_db()
        users = list(db.users.find().sort('created_at', -1))
        # Ensure default role if missing
        for u in users:
            if not u.get('role'):
                u['role'] = 'user'
        return serialize_doc(users)

    def change_user_role(self, user_id, new_role):
        if new_role not in ['user', 'admin']:
            return False, "Invalid role specified."

        u_oid = to_object_id(user_id)
        if not u_oid:
            return False, "Invalid user ID."

        db = get_db()
        target_user = db.users.find_one({'_id': u_oid})
        if not target_user:
            return False, "User not found."

        # Safety check: Do not allow removing the final administrator account!
        current_role = target_user.get('role', 'user')
        if current_role == 'admin' and new_role == 'user':
            admin_count = db.users.count_documents({'role': 'admin'})
            if admin_count <= 1:
                return False, "Cannot demote the last remaining administrator account."

        db.users.update_one({'_id': u_oid}, {'$set': {'role': new_role}})
        return True, f"User role updated to '{new_role}'."

    def delete_user(self, user_id):
        u_oid = to_object_id(user_id)
        if not u_oid:
            return False, "Invalid user ID."

        db = get_db()
        target_user = db.users.find_one({'_id': u_oid})
        if not target_user:
            return False, "User not found."

        # Safety check: Do not allow deleting the final administrator account!
        if target_user.get('role') == 'admin':
            admin_count = db.users.count_documents({'role': 'admin'})
            if admin_count <= 1:
                return False, "Cannot delete the last remaining administrator account."

        db.users.delete_one({'_id': u_oid})
        return True, "User deleted successfully."

    # Movie Management
    def get_all_movies(self):
        db = get_db()
        movies = list(db.movies.find().sort('created_at', -1))
        return serialize_doc(movies)

    def add_movie(self, data):
        db = get_db()
        title = data.get('title', '').strip()
        if not title:
            return False, "Movie title is required."

        genre = data.get('genre', [])
        if isinstance(genre, str):
            genre = [g.strip() for g in genre.split(',') if g.strip()]

        movie_doc = {
            'title': title,
            'poster_url': data.get('poster_url') or data.get('poster', ''),
            'banner_url': data.get('banner_url') or data.get('backdrop', ''),
            'description': data.get('description', ''),
            'language': data.get('language', 'English'),
            'genre': genre,
            'duration': data.get('duration', '2h 00m'),
            'certificate': data.get('certificate') or data.get('certification', 'UA'),
            'rating': float(data.get('rating', 4.5)),
            'status': data.get('status', 'now_showing'), # 'now_showing', 'coming_soon', 'ended'
            'release_date': data.get('release_date') or datetime.now().strftime('%Y-%m-%d'),
            'cast': data.get('cast', []),
            'director': data.get('director', ''),
            'created_at': datetime.now(timezone.utc)
        }

        res = db.movies.insert_one(movie_doc)
        movie_doc['_id'] = res.inserted_id
        return True, serialize_doc(movie_doc)

    def update_movie(self, movie_id, data):
        m_oid = to_object_id(movie_id)
        if not m_oid:
            return False, "Invalid movie ID."

        db = get_db()
        updates = {}

        if 'title' in data and data['title'].strip():
            updates['title'] = data['title'].strip()
        if 'poster_url' in data:
            updates['poster_url'] = data['poster_url']
            updates['poster'] = data['poster_url']
        if 'banner_url' in data:
            updates['banner_url'] = data['banner_url']
            updates['backdrop'] = data['banner_url']
        if 'description' in data:
            updates['description'] = data['description']
        if 'language' in data:
            updates['language'] = data['language']
        if 'genre' in data:
            genre = data['genre']
            if isinstance(genre, str):
                genre = [g.strip() for g in genre.split(',') if g.strip()]
            updates['genre'] = genre
        if 'duration' in data:
            updates['duration'] = data['duration']
        if 'certificate' in data:
            updates['certificate'] = data['certificate']
        if 'rating' in data:
            try:
                updates['rating'] = float(data['rating'])
            except (ValueError, TypeError):
                pass
        if 'status' in data:
            updates['status'] = data['status']
        if 'release_date' in data:
            updates['release_date'] = data['release_date']

        if updates:
            db.movies.update_one({'_id': m_oid}, {'$set': updates})

        updated = db.movies.find_one({'_id': m_oid})
        return True, serialize_doc(updated)

    def delete_movie(self, movie_id):
        m_oid = to_object_id(movie_id)
        if not m_oid:
            return False, "Invalid movie ID."

        db = get_db()
        db.movies.delete_one({'_id': m_oid})
        # Clean up related shows and seats
        shows = list(db.shows.find({'movie_id': m_oid}))
        show_ids = [s['_id'] for s in shows]
        if show_ids:
            db.seats.delete_many({'show_id': {'$in': show_ids}})
            db.shows.delete_many({'movie_id': m_oid})

        return True, "Movie and associated showtimes removed successfully."

    # Theatre Management
    def get_all_theatres(self):
        db = get_db()
        theatres = list(db.theatres.find().sort('name', 1))
        return serialize_doc(theatres)

    def add_theatre(self, data):
        db = get_db()
        name = data.get('name') or data.get('theatre_name', '').strip()
        if not name:
            return False, "Theatre name is required."

        theatre_doc = {
            'name': name,
            'location': data.get('location', 'Kochi'),
            'address': data.get('address', 'Kochi, Kerala'),
            'city': data.get('city', 'Kochi'),
            'screens': int(data.get('screens', 4)),
            'seating_capacity': int(data.get('seating_capacity', 120)),
            'distance': data.get('distance', '4.0 km'),
            'created_at': datetime.now(timezone.utc)
        }

        res = db.theatres.insert_one(theatre_doc)
        theatre_doc['_id'] = res.inserted_id
        return True, serialize_doc(theatre_doc)

    def update_theatre(self, theatre_id, data):
        t_oid = to_object_id(theatre_id)
        if not t_oid:
            return False, "Invalid theatre ID."

        db = get_db()
        updates = {}
        if 'name' in data or 'theatre_name' in data:
            updates['name'] = (data.get('name') or data.get('theatre_name')).strip()
        if 'location' in data:
            updates['location'] = data['location'].strip()
        if 'address' in data:
            updates['address'] = data['address'].strip()
        if 'city' in data:
            updates['city'] = data['city'].strip()
        if 'screens' in data:
            updates['screens'] = int(data['screens'])
        if 'seating_capacity' in data:
            updates['seating_capacity'] = int(data['seating_capacity'])

        if updates:
            db.theatres.update_one({'_id': t_oid}, {'$set': updates})

        updated = db.theatres.find_one({'_id': t_oid})
        return True, serialize_doc(updated)

    def delete_theatre(self, theatre_id):
        t_oid = to_object_id(theatre_id)
        if not t_oid:
            return False, "Invalid theatre ID."

        db = get_db()
        db.theatres.delete_one({'_id': t_oid})
        shows = list(db.shows.find({'theatre_id': t_oid}))
        show_ids = [s['_id'] for s in shows]
        if show_ids:
            db.seats.delete_many({'show_id': {'$in': show_ids}})
            db.shows.delete_many({'theatre_id': t_oid})

        return True, "Theatre and associated showtimes removed successfully."

    # Showtime Management
    def add_showtime(self, movie_id, theatre_id, screen, date_str, time_str, price=220):
        m_oid = to_object_id(movie_id)
        t_oid = to_object_id(theatre_id)
        if not m_oid or not t_oid:
            return False, "Invalid movie or theatre selection."

        db = get_db()
        movie = db.movies.find_one({'_id': m_oid})
        theatre = db.theatres.find_one({'_id': t_oid})
        if not movie or not theatre:
            return False, "Selected movie or theatre does not exist."

        show_doc = {
            'movie_id': m_oid,
            'theatre_id': t_oid,
            'screen': screen or 'Screen 1',
            'date': date_str,
            'time': time_str,
            'format': '2D',
            'price': float(price),
            'created_at': datetime.now(timezone.utc)
        }

        res = db.shows.insert_one(show_doc)
        show_id = res.inserted_id

        # Generate seats grid for showtime
        from services.seat_service import seat_service
        seat_service.generate_seats_for_show(show_id, base_price=int(price))

        show_doc['_id'] = show_id
        return True, serialize_doc(show_doc)

    def delete_showtime(self, show_id):
        s_oid = to_object_id(show_id)
        if not s_oid:
            return False, "Invalid showtime ID."

        db = get_db()
        db.seats.delete_many({'show_id': s_oid})
        db.shows.delete_one({'_id': s_oid})
        return True, "Showtime deleted successfully."

    # Booking & Payment Management
    def normalize_booking(self, b):
        b = serialize_doc(b)
        if not isinstance(b, dict):
            return b
        b['booking_id'] = b.get('booking_id') or b.get('bookingId') or ''
        b['transaction_id'] = b.get('transaction_id') or b.get('transactionId') or b.get('booking_id') or b.get('bookingId') or ''
        b['movie_title'] = b.get('movie_title') or b.get('movieTitle') or 'Movie Ticket'
        b['movie_poster'] = b.get('movie_poster') or b.get('moviePoster') or ''
        b['theatre_name'] = b.get('theatre_name') or b.get('theatreName') or 'Cinema'
        b['location'] = b.get('location') or ''
        b['date'] = b.get('date') or b.get('show_date') or b.get('booking_date') or ''
        b['time'] = b.get('time') or b.get('showtime') or b.get('show_time') or ''
        b['showtime'] = b['time']
        
        seats = b.get('seats') or []
        if isinstance(seats, str):
            seats = [s.strip() for s in seats.split(',') if s.strip()]
        b['seats'] = seats
        b['ticket_count'] = b.get('ticket_count') or len(seats)
        
        try:
            b['total_amount'] = float(b.get('total_amount') or b.get('totalAmount') or 0.0)
        except (ValueError, TypeError):
            b['total_amount'] = 0.0

        b['booking_status'] = (b.get('booking_status') or b.get('bookingStatus') or 'confirmed').lower()
        b['payment_status'] = (b.get('payment_status') or b.get('paymentStatus') or 'paid').lower()
        b['screen'] = b.get('screen') or 'Screen 1'
        return b

    def _parse_time_mins(self, time_str):
        if not time_str:
            return 99999
        t_clean = str(time_str).strip().upper()
        for fmt in ('%I:%M %p', '%I:%M%p', '%H:%M'):
            try:
                dt = datetime.strptime(t_clean, fmt)
                return dt.hour * 60 + dt.minute
            except ValueError:
                pass
        return 99999

    def get_admin_bookings_filtered(self, date_str=None, start_date_str=None, status='all', search=None):
        db = get_db()
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')

        if not date_str:
            date_str = today_str

        try:
            selected_date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except Exception:
            selected_date_obj = today
            date_str = today_str

        if start_date_str:
            try:
                start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d')
            except Exception:
                start_date_obj = selected_date_obj - timedelta(days=selected_date_obj.weekday())
        else:
            start_date_obj = selected_date_obj - timedelta(days=selected_date_obj.weekday())

        start_date_str = start_date_obj.strftime('%Y-%m-%d')
        end_date_obj = start_date_obj + timedelta(days=6)
        end_date_str = end_date_obj.strftime('%Y-%m-%d')

        week_days = []
        week_dates = []
        for i in range(7):
            d = start_date_obj + timedelta(days=i)
            d_str = d.strftime('%Y-%m-%d')
            week_dates.append(d_str)
            week_days.append({
                'date_str': d_str,
                'day_name': d.strftime('%a').upper(),
                'day_num': d.strftime('%d'),
                'month_name': d.strftime('%b').upper(),
                'full_formatted': d.strftime('%A, %d %B %Y'),
                'is_selected': (d_str == date_str),
                'is_today': (d_str == today_str)
            })

        window_raw_bookings = list(db.bookings.find({
            '$or': [
                {'date': {'$in': week_dates}},
                {'show_date': {'$in': week_dates}}
            ]
        }))

        weekly_counts = {d_str: 0 for d_str in week_dates}
        for rb in window_raw_bookings:
            b_date = rb.get('date') or rb.get('show_date') or ''
            if b_date in weekly_counts:
                weekly_counts[b_date] += 1

        for wd in week_days:
            wd['count'] = weekly_counts.get(wd['date_str'], 0)

        query = {
            '$or': [
                {'date': date_str},
                {'show_date': date_str}
            ]
        }

        if status and status.lower() != 'all':
            query['$and'] = [
                {
                    '$or': [
                        {'booking_status': {'$regex': f"^{status}$", '$options': 'i'}},
                        {'bookingStatus': {'$regex': f"^{status}$", '$options': 'i'}}
                    ]
                }
            ]

        raw_bookings = list(db.bookings.find(query))
        normalized = [self.normalize_booking(b) for b in raw_bookings]

        if search and search.strip():
            s_term = search.strip().lower()
            filtered = []
            for b in normalized:
                match_id = s_term in b.get('booking_id', '').lower()
                match_txn = s_term in b.get('transaction_id', '').lower()
                match_movie = s_term in b.get('movie_title', '').lower()
                match_theatre = s_term in b.get('theatre_name', '').lower()
                if match_id or match_txn or match_movie or match_theatre:
                    filtered.append(b)
            normalized = filtered

        normalized.sort(key=lambda b: (self._parse_time_mins(b.get('time')), str(b.get('created_at') or '')))

        total_bookings = len(normalized)
        seats_reserved = sum(b.get('ticket_count', 0) for b in normalized)
        confirmed_count = sum(1 for b in normalized if b.get('booking_status') == 'confirmed')
        total_revenue = sum(b.get('total_amount', 0.0) for b in normalized if b.get('booking_status') == 'confirmed')

        formatted_date = selected_date_obj.strftime('%A, %d %B %Y')
        range_formatted = f"{start_date_obj.strftime('%d %b')} – {end_date_obj.strftime('%d %b %Y')}"

        return {
            'selected_date': date_str,
            'formatted_date': formatted_date,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'range_formatted': range_formatted,
            'prev_week_start': (start_date_obj - timedelta(days=7)).strftime('%Y-%m-%d'),
            'next_week_start': (start_date_obj + timedelta(days=7)).strftime('%Y-%m-%d'),
            'today_date': today_str,
            'week_days': week_days,
            'bookings': normalized,
            'summary': {
                'total_bookings': total_bookings,
                'seats_reserved': seats_reserved,
                'confirmed_count': confirmed_count,
                'total_revenue': round(total_revenue, 2),
                'total_revenue_formatted': f"₹{total_revenue:,.2f}"
            }
        }

    def get_all_bookings(self):
        db = get_db()
        raw = list(db.bookings.find().sort('created_at', -1))
        return [self.normalize_booking(b) for b in raw]

    def get_all_payments(self):
        db = get_db()
        payments = list(db.payments.find().sort('created_at', -1))
        
        user_ids = list({p.get('user_id') for p in payments if p.get('user_id')})
        u_oids = [to_object_id(uid) for uid in user_ids if to_object_id(uid)]
        users_map = {u['_id']: serialize_doc(u) for u in db.users.find({'_id': {'$in': u_oids}})}

        enriched = []
        for p in payments:
            sp = serialize_doc(p)
            u_oid = to_object_id(p.get('user_id'))
            if u_oid and u_oid in users_map:
                sp['user_name'] = users_map[u_oid].get('name')
                sp['user_email'] = users_map[u_oid].get('email')
            enriched.append(sp)

        return enriched

admin_service = AdminService()

import uuid
from datetime import datetime, timezone
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc
from services.seat_service import seat_service
from services.show_service import show_service
from services.payment_service import payment_service

class BookingService:
    def create_booking(self, user_id, show_id, seat_numbers, food_items=None, payment_method='UPI'):
        db = get_db()
        u_oid = to_object_id(user_id)
        s_oid = to_object_id(show_id)

        if not u_oid or not s_oid:
            return None, "Invalid user or show ID."

        show = show_service.get_show_by_id(show_id)
        if not show:
            return None, "Showtime not found."

        # 1. Atomic seat reservation check
        success, msg = seat_service.book_seats_atomic(show_id, seat_numbers, user_id)
        if not success:
            return None, msg

        # 2. Calculate seat ticket pricing
        seats_db = list(db.seats.find({
            'show_id': s_oid,
            'seat_number': {'$in': seat_numbers}
        }))
        ticket_amount = sum(s.get('price', show.get('price', 220)) for s in seats_db)

        # 3. Calculate food pricing
        food_amount = 0
        parsed_food = []
        if food_items and isinstance(food_items, list):
            for item in food_items:
                f_name = item.get('name')
                f_qty = int(item.get('qty', 1))
                f_price = float(item.get('price', 0))
                food_amount += f_price * f_qty
                parsed_food.append({
                    'name': f_name,
                    'qty': f_qty,
                    'price': f_price
                })

        subtotal = ticket_amount + food_amount
        convenience_fee = 30.0
        total_amount = round(subtotal + convenience_fee, 2)

        booking_code = f"CTBK{uuid.uuid4().hex[:6].upper()}"
        txn_id = f"CT{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"

        movie_data = show.get('movie') or {}
        theatre_data = show.get('theatre') or {}

        booking_doc = {
            'booking_id': booking_code,
            'transaction_id': txn_id,
            'user_id': u_oid,
            'show_id': s_oid,
            'movie_id': to_object_id(movie_data.get('id') or movie_data.get('_id')),
            'theatre_id': to_object_id(theatre_data.get('id') or theatre_data.get('_id')),
            'movie_title': movie_data.get('title', 'Movie Ticket'),
            'movie_poster': movie_data.get('poster_url') or movie_data.get('poster'),
            'theatre_name': theatre_data.get('name', 'Cinema'),
            'location': theatre_data.get('address') or theatre_data.get('location', 'Kochi'),
            'date': show.get('date'),
            'time': show.get('time'),
            'showtime': show.get('time'),
            'screen': show.get('screen', 'Screen 1'),
            'seats': seat_numbers,
            'ticket_count': len(seat_numbers),
            'ticket_price': ticket_amount,
            'food_items': parsed_food,
            'food_amount': food_amount,
            'subtotal': subtotal,
            'convenience_fee': convenience_fee,
            'total_amount': total_amount,
            'payment_method': payment_method,
            'payment_status': 'paid',
            'booking_status': 'confirmed',
            'created_at': datetime.now(timezone.utc)
        }

        res = db.bookings.insert_one(booking_doc)
        booking_doc['_id'] = res.inserted_id

        # 4. Create Payment Log
        payment_service.process_demo_payment(
            booking_id=res.inserted_id,
            user_id=user_id,
            amount=total_amount,
            payment_method=payment_method
        )

        return serialize_doc(booking_doc), "Booking created successfully"


    def get_user_bookings(self, user_id):
        u_oid = to_object_id(user_id)
        if not u_oid:
            return []
        db = get_db()
        bookings = list(db.bookings.find({'user_id': u_oid}).sort('created_at', -1))
        return serialize_doc(bookings)

    def get_booking_by_id(self, booking_id):
        db = get_db()
        booking = None
        b_oid = to_object_id(booking_id)
        if b_oid:
            booking = db.bookings.find_one({'_id': b_oid})
        if not booking:
            booking = db.bookings.find_one({'booking_id': str(booking_id)})

        if not booking:
            return None

        from utils.qr_generator import generate_qr_code_base64
        serialized = serialize_doc(booking)
        b_code = serialized.get('booking_id') or str(serialized.get('id', ''))
        serialized['qr_code'] = generate_qr_code_base64(f"CINETICKETS-TICKET-VERIFY-{b_code}")
        return serialized


booking_service = BookingService()


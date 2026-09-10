from datetime import datetime, timezone
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc

class SeatService:
    ROWS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K']
    SEATS_PER_ROW = 10

    def generate_seats_for_show(self, show_id, base_price=220):
        s_oid = to_object_id(show_id)
        if not s_oid:
            return []

        db = get_db()
        seat_docs = []

        for row in self.ROWS:
            category = 'Standard'
            row_price = base_price
            if row in ['A', 'B', 'C', 'D']:
                category = 'Standard'
                row_price = base_price
            elif row in ['E', 'F', 'G', 'H']:
                category = 'Premium'
                row_price = int(base_price * 1.25)
            elif row in ['I', 'J', 'K']:
                category = 'VIP'
                row_price = int(base_price * 1.6)

            for num in range(1, self.SEATS_PER_ROW + 1):
                seat_num = f"{row}{num}"
                seat_docs.append({
                    'show_id': s_oid,
                    'seat_number': seat_num,
                    'row': row,
                    'number': num,
                    'category': category,
                    'price': row_price,
                    'status': 'available'
                })

        if seat_docs:
            existing_count = db.seats.count_documents({'show_id': s_oid})
            if existing_count < 110:
                db.seats.delete_many({'show_id': s_oid})
                db.seats.insert_many(seat_docs)

        return self.get_seats_for_show(show_id)

    def get_seats_for_show(self, show_id):
        s_oid = to_object_id(show_id)
        if not s_oid:
            return []

        db = get_db()
        seats = list(db.seats.find({'show_id': s_oid}))

        if len(seats) < 110:
            show = db.shows.find_one({'_id': s_oid})
            base_price = show.get('price', 220) if show else 220
            return self.generate_seats_for_show(show_id, base_price=base_price)

        return serialize_doc(seats)


    def book_seats_atomic(self, show_id, seat_numbers, user_id):
        """
        Atomic seat booking verification on MongoDB Atlas.
        Verifies every selected seat has status 'available'.
        Updates selected seats to status 'booked' in MongoDB.
        """
        s_oid = to_object_id(show_id)
        u_oid = to_object_id(user_id)
        if not s_oid:
            return False, "Invalid show ID."

        db = get_db()
        now_dt = datetime.now(timezone.utc)

        existing_seats = list(db.seats.find({
            'show_id': s_oid,
            'seat_number': {'$in': seat_numbers}
        }))

        seats_map = {s['seat_number']: s for s in existing_seats}

        unavailable = []
        for sn in seat_numbers:
            seat_obj = seats_map.get(sn)
            if not seat_obj or seat_obj.get('status') != 'available':
                unavailable.append(sn)

        if unavailable:
            return False, "One or more selected seats are no longer available."

        update_result = db.seats.update_many(
            {
                'show_id': s_oid,
                'seat_number': {'$in': seat_numbers},
                'status': 'available'
            },
            {
                '$set': {
                    'status': 'booked',
                    'booked_by': u_oid or str(user_id),
                    'booked_at': now_dt
                }
            }
        )

        if update_result.modified_count != len(seat_numbers):
            # Rollback on conflict
            db.seats.update_many(
                {'show_id': s_oid, 'seat_number': {'$in': seat_numbers}},
                {'$set': {'status': 'available', 'booked_by': None}}
            )
            return False, "One or more selected seats are no longer available."

        return True, "Seats successfully locked."

seat_service = SeatService()

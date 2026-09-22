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

    def toggle_block_seat(self, show_id, seat_number):
        s_oid = to_object_id(show_id)
        if not s_oid:
            return False, "Invalid showtime ID."

        db = get_db()
        seat = db.seats.find_one({'show_id': s_oid, 'seat_number': seat_number})
        if not seat:
            # Fallback if seat_number matches number/row
            seats = list(db.seats.find({'show_id': s_oid}))
            seat = next((s for s in seats if s.get('seat_number') == seat_number), None)
        if not seat:
            return False, f"Seat '{seat_number}' not found."

        current_status = (seat.get('status') or 'available').lower()
        if current_status == 'booked' or seat.get('is_booked'):
            return False, f"Seat {seat_number} has an active booking and cannot be blocked or modified."

        new_status = 'blocked' if current_status == 'available' else 'available'
        db.seats.update_one(
            {'_id': seat['_id']},
            {'$set': {'status': new_status}}
        )

        # Update showtime available_seats count in db.shows
        all_seats = list(db.seats.find({'show_id': s_oid}))
        avail_count = sum(1 for s in all_seats if (s.get('status') or 'available').lower() == 'available')
        db.shows.update_one({'_id': s_oid}, {'$set': {'available_seats': avail_count}})

        return True, f"Seat {seat_number} status updated to '{new_status.upper()}'."

    def get_seat_stats(self, show_id):
        seats = self.get_seats_for_show(show_id)
        total = len(seats)
        available = sum(1 for s in seats if (s.get('status') or 'available').lower() == 'available')
        booked = sum(1 for s in seats if (s.get('status') or '').lower() == 'booked' or s.get('is_booked'))
        held = sum(1 for s in seats if (s.get('status') or '').lower() == 'held')
        blocked = sum(1 for s in seats if (s.get('status') or '').lower() == 'blocked')

        return {
            'total': total,
            'available': available,
            'booked': booked,
            'held': held,
            'blocked': blocked
        }

seat_service = SeatService()

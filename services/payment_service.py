import uuid
from datetime import datetime, timezone
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc

class PaymentService:
    def process_demo_payment(self, booking_id, user_id, amount, payment_method):
        db = get_db()
        b_oid = to_object_id(booking_id)
        u_oid = to_object_id(user_id)

        txn_id = f"TXN{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"

        payment_doc = {
            'booking_id': b_oid or str(booking_id),
            'user_id': u_oid or str(user_id),
            'amount': float(amount),
            'method': payment_method or 'UPI',
            'status': 'success',
            'transaction_id': txn_id,
            'created_at': datetime.now(timezone.utc)
        }

        res = db.payments.insert_one(payment_doc)
        payment_doc['_id'] = res.inserted_id
        return serialize_doc(payment_doc)

payment_service = PaymentService()

from flask import Blueprint, jsonify, request
from services.payment_service import payment_service
from utils.auth import get_current_user, login_required

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route('/api/payment/process', methods=['POST'])
@login_required
def api_process_payment():
    user = get_current_user()
    data = request.get_json() or {}
    booking_id = data.get('booking_id')
    amount = data.get('amount')
    method = data.get('method', 'PhonePe')

    if not amount:
        return jsonify({'success': False, 'message': 'Payment amount is required.'}), 400

    payment = payment_service.process_demo_payment(
        booking_id=booking_id or 'TEMP',
        user_id=user['id'],
        amount=amount,
        payment_method=method
    )

    return jsonify({'success': True, 'message': 'Payment processed successfully.', 'payment': payment})

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from services.show_service import show_service
from services.seat_service import seat_service
from services.booking_service import booking_service
from utils.auth import get_current_user, login_required

booking_bp = Blueprint('booking_bp', __name__)

@booking_bp.route('/booking/seats/<show_id>')
@booking_bp.route('/seats/<show_id>')
@booking_bp.route('/seats')
@login_required
def seats_page(show_id=None):
    if not show_id:
        show_id = request.args.get('show_id') or request.args.get('showId')

    # If show_id was not explicitly passed, try lookup by movie_id + theatre_id + showtime
    if not show_id:
        movie_id = request.args.get('movie_id') or request.args.get('movieId')
        theatre_id = request.args.get('theatre_id') or request.args.get('theatreId')
        time_str = request.args.get('showtime') or request.args.get('time')
        date_str = request.args.get('date')

        if movie_id and theatre_id and time_str:
            show = show_service.find_or_create_show(movie_id, theatre_id, time_str, date_str)
            if show:
                show_id = show['id']

    if not show_id:
        flash("Please select a valid movie and showtime.", "warning")
        return redirect(url_for('movie_bp.movies_page'))

    show = show_service.get_show_by_id(show_id)
    if not show:
        return render_template('error.html', error_message="Showtime not found."), 404

    seats = seat_service.get_seats_for_show(show_id)
    return render_template('seats.html', show=show, seats=seats)

@booking_bp.route('/booking/summary')
@login_required
def booking_summary():
    show_id = request.args.get('show_id')
    show = show_service.get_show_by_id(show_id) if show_id else None
    return render_template('summary.html', show=show)

@booking_bp.route('/booking/food')
@booking_bp.route('/food-drinks')
@login_required
def food_drinks_page():
    return render_template('food_drinks.html')

@booking_bp.route('/booking/payment')
@booking_bp.route('/payment')
@login_required
def payment_page():
    show_id = request.args.get('show_id')
    show = show_service.get_show_by_id(show_id) if show_id else None
    return render_template('payment.html', show=show)

@booking_bp.route('/booking/success/<booking_id>')
@booking_bp.route('/booking-success')
@login_required
def booking_success(booking_id=None):
    if not booking_id:
        booking_id = request.args.get('booking_id')

    booking = booking_service.get_booking_by_id(booking_id) if booking_id else None
    if not booking:
        flash("Booking details not found.", "warning")
        return redirect(url_for('booking_bp.user_bookings'))

    return render_template('booking_success.html', booking=booking)

@booking_bp.route('/ticket/<booking_id>')
@booking_bp.route('/booking/<booking_id>/ticket')
@login_required
def digital_ticket(booking_id):
    booking = booking_service.get_booking_by_id(booking_id)
    if not booking:
        flash("Ticket not found.", "danger")
        return redirect(url_for('booking_bp.user_bookings'))

    # Security check: User can only view their own ticket (unless admin)
    user = get_current_user()
    if user['role'] != 'admin' and str(booking.get('user_id')) != str(user['id']):
        flash("Access denied. You can only view your own tickets.", "danger")
        return redirect(url_for('booking_bp.user_bookings'))

    return render_template('ticket.html', booking=booking)

@booking_bp.route('/my-bookings')
@booking_bp.route('/bookings')
@login_required
def user_bookings():
    user = get_current_user()
    bookings = booking_service.get_user_bookings(user['id'])
    return render_template('bookings.html', bookings=bookings)

# API Endpoints
@booking_bp.route('/api/bookings/create', methods=['POST'])
@login_required
def api_create_booking():
    user = get_current_user()
    data = request.get_json() or {}
    show_id = data.get('show_id') or data.get('showId')
    seat_numbers = data.get('seats', [])
    food_items = data.get('food_items') or data.get('foodItems', [])
    payment_method = data.get('payment_method') or data.get('paymentMethod', 'UPI')

    if not show_id or not seat_numbers:
        return jsonify({'success': False, 'message': 'Showtime and seat selection are required.'}), 400

    if len(seat_numbers) > 8:
        return jsonify({'success': False, 'message': 'Maximum 8 seats allowed per booking.'}), 400

    booking, msg = booking_service.create_booking(
        user_id=user['id'],
        show_id=show_id,
        seat_numbers=seat_numbers,
        food_items=food_items,
        payment_method=payment_method
    )

    if not booking:
        return jsonify({'success': False, 'message': msg}), 409

    return jsonify({'success': True, 'message': msg, 'booking': booking})

@booking_bp.route('/api/bookings', methods=['GET'])
@login_required
def api_get_bookings():
    user = get_current_user()
    bookings = booking_service.get_user_bookings(user['id'])
    return jsonify({'success': True, 'bookings': bookings})

@booking_bp.route('/api/bookings/<booking_id>', methods=['GET'])
@login_required
def api_get_booking_detail(booking_id):
    booking = booking_service.get_booking_by_id(booking_id)
    if not booking:
        return jsonify({'success': False, 'message': 'Booking not found'}), 404
    return jsonify({'success': True, 'booking': booking})

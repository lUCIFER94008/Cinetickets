import os
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from services.mongodb_service import get_db
from services.admin_service import admin_service
from services.show_service import show_service
from services.seat_service import seat_service
from utils.auth import admin_required, get_current_user
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin_bp', __name__)

# Public First Admin Setup Endpoint
@admin_bp.route('/admin/setup', methods=['GET', 'POST'])
def admin_setup():
    db = get_db()
    existing_admin_count = db.users.count_documents({'role': 'admin'})

    if request.method == 'POST':
        setup_key = request.form.get('setup_key') or (request.get_json() or {}).get('setup_key')
        env_key = os.getenv('ADMIN_SETUP_KEY')

        # Key verification
        if not env_key or setup_key != env_key:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid setup key.'}), 403
            flash('Invalid admin setup key.', 'danger')
            return render_template('admin/setup.html', existing_admin_count=existing_admin_count)

        # Prevent duplicate setup if admin already exists
        if existing_admin_count > 0:
            msg = "An administrator account already exists."
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'warning')
            return render_template('admin/setup.html', existing_admin_count=existing_admin_count)

        name = request.form.get('name') or (request.get_json() or {}).get('name')
        email = request.form.get('email') or (request.get_json() or {}).get('email')
        phone = request.form.get('phone') or (request.get_json() or {}).get('phone')
        password = request.form.get('password') or (request.get_json() or {}).get('password')

        if not name or not email or not password:
            msg = "Name, email, and password are required."
            if request.is_json:
                return jsonify({'success': False, 'message': msg}), 400
            flash(msg, 'danger')
            return render_template('admin/setup.html', existing_admin_count=existing_admin_count)

        # Create admin user
        admin_doc = {
            'name': name.strip(),
            'email': email.strip().lower(),
            'phone': phone.strip() if phone else '',
            'password_hash': generate_password_hash(password),
            'role': 'admin'
        }
        res = db.users.insert_one(admin_doc)

        if request.is_json:
            return jsonify({'success': True, 'message': 'Administrator created successfully!', 'admin_id': str(res.inserted_id)})

        flash('First Administrator created successfully! Please log in.', 'success')
        return redirect(url_for('auth_bp.login_page'))

    return render_template('admin/setup.html', existing_admin_count=existing_admin_count)

# Admin Dashboard
@admin_bp.route('/admin')
@admin_required
def admin_dashboard():
    stats = admin_service.get_dashboard_stats()
    recent_bookings = admin_service.get_all_bookings()[:5]
    return render_template('admin/dashboard.html', stats=stats, recent_bookings=recent_bookings)

# User Management
@admin_bp.route('/admin/users')
@admin_required
def admin_users():
    users = admin_service.get_all_users()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/role/<user_id>', methods=['POST'])
@admin_required
def change_role(user_id):
    new_role = request.form.get('role') or (request.get_json() or {}).get('role')
    success, msg = admin_service.change_user_role(user_id, new_role)
    if request.is_json:
        return jsonify({'success': success, 'message': msg})
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_users'))

@admin_bp.route('/admin/users/delete/<user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    success, msg = admin_service.delete_user(user_id)
    if request.is_json:
        return jsonify({'success': success, 'message': msg})
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_users'))

# Movie Management
@admin_bp.route('/admin/movies')
@admin_required
def admin_movies():
    movies = admin_service.get_all_movies()
    return render_template('admin/movies.html', movies=movies)

@admin_bp.route('/admin/movies/add', methods=['POST'])
@admin_required
def add_movie():
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    success, res = admin_service.add_movie(data)
    if request.is_json:
        return jsonify({'success': success, 'result': res if success else None, 'message': res if not success else 'Movie added successfully'})
    flash('Movie added successfully!' if success else str(res), 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_movies'))

@admin_bp.route('/admin/movies/edit/<movie_id>', methods=['POST'])
@admin_required
def edit_movie(movie_id):
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    success, res = admin_service.update_movie(movie_id, data)
    if request.is_json:
        return jsonify({'success': success, 'result': res if success else None, 'message': res if not success else 'Movie updated successfully'})
    flash('Movie updated successfully!' if success else str(res), 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_movies'))

@admin_bp.route('/admin/movies/delete/<movie_id>', methods=['POST'])
@admin_required
def delete_movie(movie_id):
    success, msg = admin_service.delete_movie(movie_id)
    if request.is_json:
        return jsonify({'success': success, 'message': msg})
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_movies'))

# Theatre Management
@admin_bp.route('/admin/theatres')
@admin_required
def admin_theatres():
    theatres = admin_service.get_all_theatres()
    return render_template('admin/theatres.html', theatres=theatres)

@admin_bp.route('/admin/theatres/add', methods=['POST'])
@admin_required
def add_theatre():
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    success, res = admin_service.add_theatre(data)
    if request.is_json:
        return jsonify({'success': success, 'result': res if success else None, 'message': res if not success else 'Theatre added successfully'})
    flash('Theatre added successfully!' if success else str(res), 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_theatres'))

@admin_bp.route('/admin/theatres/edit/<theatre_id>', methods=['POST'])
@admin_required
def edit_theatre(theatre_id):
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    success, res = admin_service.update_theatre(theatre_id, data)
    if request.is_json:
        return jsonify({'success': success, 'result': res if success else None, 'message': res if not success else 'Theatre updated successfully'})
    flash('Theatre updated successfully!' if success else str(res), 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_theatres'))

@admin_bp.route('/admin/theatres/delete/<theatre_id>', methods=['POST'])
@admin_required
def delete_theatre(theatre_id):
    success, msg = admin_service.delete_theatre(theatre_id)
    if request.is_json:
        return jsonify({'success': success, 'message': msg})
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_theatres'))

# Showtime Management
@admin_bp.route('/admin/showtimes')
@admin_required
def admin_showtimes():
    shows = show_service.get_shows()
    movies = admin_service.get_all_movies()
    theatres = admin_service.get_all_theatres()
    return render_template('admin/showtimes.html', shows=shows, movies=movies, theatres=theatres)

@admin_bp.route('/admin/showtimes/add', methods=['POST'])
@admin_required
def add_showtime():
    data = request.form.to_dict() if request.form else (request.get_json() or {})
    movie_id = data.get('movie_id')
    theatre_id = data.get('theatre_id')
    screen = data.get('screen', 'Screen 1')
    date_str = data.get('date')
    time_str = data.get('time')
    price = data.get('price', 220)

    success, res = admin_service.add_showtime(movie_id, theatre_id, screen, date_str, time_str, price)
    if request.is_json:
        return jsonify({'success': success, 'result': res if success else None, 'message': res if not success else 'Showtime added successfully'})
    flash('Showtime scheduled successfully!' if success else str(res), 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_showtimes'))

@admin_bp.route('/admin/showtimes/delete/<show_id>', methods=['POST'])
@admin_required
def delete_showtime(show_id):
    success, msg = admin_service.delete_showtime(show_id)
    if request.is_json:
        return jsonify({'success': success, 'message': msg})
    flash(msg, 'success' if success else 'danger')
    return redirect(url_for('admin_bp.admin_showtimes'))

# Booking & Payment Management
@admin_bp.route('/admin/bookings')
@admin_required
def admin_bookings():
    bookings = admin_service.get_all_bookings()
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/admin/payments')
@admin_required
def admin_payments():
    payments = admin_service.get_all_payments()
    return render_template('admin/payments.html', payments=payments)

# Seat Availability Inspection
@admin_bp.route('/admin/seats')
@admin_required
def admin_seats():
    show_id = request.args.get('show_id')
    shows = show_service.get_shows()
    selected_show = show_service.get_show_by_id(show_id) if show_id else (shows[0] if shows else None)
    seats = seat_service.get_seats_for_show(selected_show['id']) if selected_show else []
    return render_template('admin/seats.html', shows=shows, selected_show=selected_show, seats=seats)

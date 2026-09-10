from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from services.auth_service import auth_service
from utils.auth import get_current_user

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if session.get('user_id'):
        return redirect(url_for('main_bp.index'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not name or not email or not phone or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        success, res = auth_service.register_user(name, email, phone, password)
        if not success:
            flash(res, 'danger')
            return render_template('register.html')

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth_bp.login_page'))

    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    next_url = request.form.get('next') or request.args.get('next')
    if session.get('user_id'):
        return redirect(next_url or url_for('main_bp.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('login.html', next_url=next_url)

        success, msg, user = auth_service.login_user(email, password)
        if not success:
            flash(msg, 'danger')
            return render_template('login.html', next_url=next_url)

        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        session['user_role'] = user.get('role', 'user')

        flash(f'Welcome back, {user["name"]}!', 'success')
        if user.get('role') == 'admin':
            return redirect(url_for('admin_bp.admin_dashboard'))

        return redirect(next_url or url_for('main_bp.index'))

    return render_template('login.html', next_url=next_url)



@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main_bp.index'))

# JSON API Endpoints
@auth_bp.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400

    success, res = auth_service.register_user(name, email, phone or '', password)
    if not success:
        return jsonify({'success': False, 'message': res}), 400

    return jsonify({'success': True, 'message': 'Registration successful!', 'user': res})

@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    success, msg, user = auth_service.login_user(email, password)
    if not success:
        return jsonify({'success': False, 'message': msg}), 401

    session['user_id'] = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    session['user_role'] = user.get('role', 'user')

    return jsonify({'success': True, 'message': 'Login successful!', 'user': user})

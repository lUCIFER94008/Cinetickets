from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from services.auth_service import auth_service
from utils.auth import get_current_user, login_required

profile_bp = Blueprint('profile_bp', __name__)

@profile_bp.route('/profile')
@login_required
def profile_page():
    user = get_current_user()
    return render_template('profile.html', user=user)

@profile_bp.route('/api/profile/update', methods=['POST'])
@login_required
def api_update_profile():
    user = get_current_user()
    data = request.get_json() or {}
    name = data.get('name')
    phone = data.get('phone')

    success, updated_user = auth_service.update_profile(user['id'], name=name, phone=phone)
    if not success:
        return jsonify({'success': False, 'message': updated_user}), 400

    return jsonify({'success': True, 'message': 'Profile updated successfully!', 'user': updated_user})

@profile_bp.route('/api/profile/change-password', methods=['POST'])
@login_required
def api_change_password():
    user = get_current_user()
    data = request.get_json() or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'success': False, 'message': 'Both old and new passwords are required.'}), 400

    success, msg = auth_service.change_password(user['id'], old_password, new_password)
    if not success:
        return jsonify({'success': False, 'message': msg}), 400

    return jsonify({'success': True, 'message': msg})

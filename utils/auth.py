from functools import wraps
from flask import session, redirect, url_for, flash, jsonify, request
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc

def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return None
    db = get_db()
    u_oid = to_object_id(user_id)
    if not u_oid:
        return None
    user = db.users.find_one({'_id': u_oid})
    if not user:
        return None
    serialized = serialize_doc(user)
    if not serialized.get('role'):
        serialized['role'] = 'user'
    return serialized

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required. Please login.'}), 401
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth_bp.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Authentication required. Please login.'}), 401
            flash('Please log in to access the Admin Panel.', 'warning')
            return redirect(url_for('auth_bp.login_page', next=request.url))

        user = get_current_user()
        if not user or user.get('role') != 'admin':
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({'success': False, 'message': 'Access denied: Admin privileges required.'}), 403
            flash('Access denied: Administrator privileges required.', 'danger')
            return redirect(url_for('main_bp.index'))

        return f(*args, **kwargs)
    return decorated_function


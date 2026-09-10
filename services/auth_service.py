from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc

class AuthService:
    def register_user(self, name, email, phone, password):
        db = get_db()
        email_clean = email.strip().lower()
        
        # Check existing
        if db.users.find_one({'email': email_clean}):
            return False, "Email address is already registered."

        user_doc = {
            'name': name.strip(),
            'email': email_clean,
            'phone': phone.strip(),
            'password_hash': generate_password_hash(password),
            'role': 'user',
            'created_at': datetime.now(timezone.utc)
        }

        res = db.users.insert_one(user_doc)
        user_doc['_id'] = res.inserted_id
        return True, serialize_doc(user_doc)

    def login_user(self, email, password):
        db = get_db()
        email_clean = email.strip().lower()
        
        user = db.users.find_one({'email': email_clean})
        if not user:
            return False, "Invalid email address or password.", None

        # Check password hash (supports both 'password_hash' and legacy 'passwordHash')
        pwd_hash = user.get('password_hash') or user.get('passwordHash')
        if not pwd_hash or not check_password_hash(pwd_hash, password):
            return False, "Invalid email address or password.", None

        return True, "Login successful!", serialize_doc(user)

    def update_profile(self, user_id, name=None, phone=None):
        u_oid = to_object_id(user_id)
        if not u_oid:
            return False, "Invalid user ID."

        db = get_db()
        updates = {}
        if name:
            updates['name'] = name.strip()
        if phone:
            updates['phone'] = phone.strip()

        if updates:
            db.users.update_one({'_id': u_oid}, {'$set': updates})

        updated_user = db.users.find_one({'_id': u_oid})
        return True, serialize_doc(updated_user)

    def change_password(self, user_id, old_password, new_password):
        u_oid = to_object_id(user_id)
        if not u_oid:
            return False, "Invalid user ID."

        db = get_db()
        user = db.users.find_one({'_id': u_oid})
        if not user:
            return False, "User not found."

        pwd_hash = user.get('password_hash') or user.get('passwordHash')
        if not check_password_hash(pwd_hash, old_password):
            return False, "Current password is incorrect."

        new_hash = generate_password_hash(new_password)
        db.users.update_one({'_id': u_oid}, {'$set': {'password_hash': new_hash}})
        return True, "Password updated successfully."

auth_service = AuthService()

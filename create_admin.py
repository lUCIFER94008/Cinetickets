import os
import sys
import argparse
from datetime import datetime, timezone
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

# Load environment variables
load_dotenv()

def create_admin(name, email, phone, password, force=False):
    from services.mongodb_service import get_db
    db = get_db()
    if db is None:
        print("❌ Error: Could not connect to MongoDB Atlas.")
        sys.exit(1)

    email_clean = email.strip().lower()
    
    # Check if admin already exists
    existing_admin_count = db.users.count_documents({'role': 'admin'})
    if existing_admin_count > 0 and not force:
        print(f"⚠️ An administrator account already exists ({existing_admin_count} found).")
        print("Use --force if you intentionally wish to add an additional administrator.")
        return False

    existing_user = db.users.find_one({'email': email_clean})
    if existing_user:
        # Upgrade existing user to admin
        db.users.update_one(
            {'_id': existing_user['_id']},
            {
                '$set': {
                    'role': 'admin',
                    'password_hash': generate_password_hash(password),
                    'name': name.strip(),
                    'phone': phone.strip()
                }
            }
        )
        print(f"✅ User '{email_clean}' successfully upgraded to Administrator role.")
        return True

    # Create new admin document
    admin_doc = {
        'name': name.strip(),
        'email': email_clean,
        'phone': phone.strip(),
        'password_hash': generate_password_hash(password),
        'role': 'admin',
        'created_at': datetime.now(timezone.utc)
    }

    res = db.users.insert_one(admin_doc)
    print(f"✅ Administrator '{email_clean}' created successfully (ID: {res.inserted_id}).")
    return True

def main():
    parser = argparse.ArgumentParser(description="CineTickets Administrator Setup Script")
    parser.add_argument("--name", default="System Administrator", help="Admin Name")
    parser.add_argument("--email", default="admin@cinetickets.com", help="Admin Email")
    parser.add_argument("--phone", default="+919876543210", help="Admin Phone")
    parser.add_argument("--password", default="Admin@123", help="Admin Password")
    parser.add_argument("--force", action="store_true", help="Force creation even if admin exists")

    args = parser.parse_args()

    print("=================================")
    print("CineTickets Admin Creation Utility")
    print("=================================")
    
    success = create_admin(
        name=args.name,
        email=args.email,
        phone=args.phone,
        password=args.password,
        force=args.force
    )

    if success:
        print("\n🎉 Setup complete. You may now log in at http://127.0.0.1:5000/login")
    else:
        print("\n❌ Setup aborted or failed.")

if __name__ == '__main__':
    main()

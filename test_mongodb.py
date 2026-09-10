import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        print("❌ Error: MONGO_URI is missing from .env file.")
        sys.exit(1)

    try:
        from services.mongodb_service import test_connection, get_db, MONGO_DB_NAME
        if test_connection():
            db = get_db()
            user_count = db.users.count_documents({})
            print("MongoDB connection successful!")
            print(f"Database: {MONGO_DB_NAME}")
            print(f"Users collection accessible: {user_count} user(s) found.")
            sys.exit(0)
        else:
            print("❌ MongoDB connection failed: Ping command unsuccessful.")
            sys.exit(1)
    except Exception as e:
        err_msg = str(e)
        if "@" in err_msg:
            parts = err_msg.split("@")
            err_msg = "[REDACTED_CREDENTIALS]@" + parts[-1]
        print(f"❌ MongoDB connection error: {err_msg}")
        sys.exit(1)

if __name__ == '__main__':
    main()

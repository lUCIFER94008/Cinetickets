import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "cinetickets")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI is missing from .env")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    socketTimeoutMS=20000
)

db = client[MONGO_DB_NAME]
_indexes_created = False

def create_indexes(database=None):
    global _indexes_created
    if _indexes_created:
        return
    database = database or db
    if database is None:
        return
    try:
        database.users.create_index([("email", ASCENDING)], unique=True)
        database.bookings.create_index([("booking_id", ASCENDING)], unique=True, sparse=True)
        database.bookings.create_index([("user_id", ASCENDING)])
        database.shows.create_index([("movie_id", ASCENDING)])
        database.shows.create_index([("theatre_id", ASCENDING)])
        database.shows.create_index([("date", ASCENDING)])
        database.seats.create_index([("show_id", ASCENDING), ("seat_number", ASCENDING)], unique=True, sparse=True)
        _indexes_created = True
        logger.info("✅ MongoDB indexes verified successfully.")
    except Exception as e:
        logger.warning(f"Note on index creation: {e}")

def get_db():
    return db

def test_connection():
    try:
        client.admin.command("ping")
        return True
    except PyMongoError:
        return False

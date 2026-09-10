from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc

class TheatreService:
    def get_theatres(self, city=None):
        db = get_db()
        filter_query = {}
        if city:
            filter_query['city'] = city
        theatres = list(db.theatres.find(filter_query))
        return serialize_doc(theatres)

    def get_theatre_by_id(self, theatre_id):
        t_oid = to_object_id(theatre_id)
        if not t_oid:
            return None
        db = get_db()
        theatre = db.theatres.find_one({'_id': t_oid})
        return serialize_doc(theatre)

theatre_service = TheatreService()

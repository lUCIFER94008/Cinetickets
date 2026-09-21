import re
from datetime import datetime, timezone
from services.mongodb_service import get_db
from utils.db_helpers import to_object_id, serialize_doc

class TheatreService:
    def get_cities(self, active_only=True):
        db = get_db()
        filter_query = {}
        if active_only:
            filter_query['active'] = True
        cities = list(db.cities.find(filter_query).sort([('is_district', -1), ('name', 1)]))
        return serialize_doc(cities)

    def get_city_by_name(self, name):
        if not name:
            return None
        db = get_db()
        city = db.cities.find_one({'name': {'$regex': f"^{re.escape(name.strip())}$", '$options': 'i'}})
        return serialize_doc(city)

    def get_city_by_id(self, city_id):
        c_oid = to_object_id(city_id)
        if not c_oid:
            return None
        db = get_db()
        city = db.cities.find_one({'_id': c_oid})
        return serialize_doc(city)

    def create_city(self, name, state="Kerala", district=None, is_district=False, active=True):
        db = get_db()
        clean_name = name.strip()
        existing = db.cities.find_one({'name': {'$regex': f"^{re.escape(clean_name)}$", '$options': 'i'}})
        if existing:
            return False, "City already exists", serialize_doc(existing)
        
        city_doc = {
            'name': clean_name,
            'state': state,
            'district': district or clean_name,
            'is_district': bool(is_district),
            'active': bool(active),
            'created_at': datetime.now(timezone.utc)
        }
        res = db.cities.insert_one(city_doc)
        city_doc['_id'] = res.inserted_id
        return True, "City created successfully", serialize_doc(city_doc)

    def update_city(self, city_id, data):
        c_oid = to_object_id(city_id)
        if not c_oid:
            return False, "Invalid city ID"
        db = get_db()
        update_doc = {}
        if 'name' in data:
            update_doc['name'] = data['name'].strip()
        if 'state' in data:
            update_doc['state'] = data['state'].strip()
        if 'district' in data:
            update_doc['district'] = data['district'].strip()
        if 'is_district' in data:
            update_doc['is_district'] = bool(data['is_district'])
        if 'active' in data:
            update_doc['active'] = bool(data['active'])

        if not update_doc:
            return False, "No valid fields to update"

        db.cities.update_one({'_id': c_oid}, {'$set': update_doc})
        return True, "City updated successfully"

    def delete_city(self, city_id):
        c_oid = to_object_id(city_id)
        if not c_oid:
            return False, "Invalid city ID"
        db = get_db()
        db.cities.delete_one({'_id': c_oid})
        return True, "City deleted successfully"

    def get_theatres(self, city=None, active_only=False):
        db = get_db()
        filter_query = {}
        if active_only:
            filter_query['active'] = True

        if city:
            c_oid = to_object_id(city)
            if c_oid:
                filter_query['$or'] = [
                    {'city_id': c_oid},
                    {'city': {'$regex': f"^{re.escape(str(city).strip())}$", '$options': 'i'}}
                ]
            else:
                filter_query['city'] = {'$regex': f"^{re.escape(str(city).strip())}$", '$options': 'i'}

        theatres = list(db.theatres.find(filter_query).sort('name', 1))
        return serialize_doc(theatres)

    def get_theatre_by_id(self, theatre_id):
        t_oid = to_object_id(theatre_id)
        if not t_oid:
            return None
        db = get_db()
        theatre = db.theatres.find_one({'_id': t_oid})
        return serialize_doc(theatre)

    def create_theatre(self, data):
        db = get_db()
        city_name = data.get('city', 'Kochi').strip()
        city_doc = db.cities.find_one({'name': {'$regex': f"^{re.escape(city_name)}$", '$options': 'i'}})
        city_id = city_doc['_id'] if city_doc else None

        theatre_doc = {
            'name': data.get('name', '').strip(),
            'city': city_name,
            'city_id': city_id,
            'district': data.get('district', city_name).strip(),
            'address': data.get('address', '').strip(),
            'screens': int(data.get('screens', 1)),
            'formats': data.get('formats', ['2D', '3D', 'Dolby Atmos']),
            'distance': data.get('distance', '2.0 km'),
            'active': bool(data.get('active', True)),
            'created_at': datetime.now(timezone.utc)
        }
        res = db.theatres.insert_one(theatre_doc)
        theatre_doc['_id'] = res.inserted_id
        return True, "Theatre created successfully", serialize_doc(theatre_doc)

    def update_theatre(self, theatre_id, data):
        t_oid = to_object_id(theatre_id)
        if not t_oid:
            return False, "Invalid theatre ID"
        db = get_db()
        update_doc = {}
        for field in ['name', 'city', 'district', 'address', 'distance']:
            if field in data and data[field] is not None:
                update_doc[field] = str(data[field]).strip()

        if 'city' in update_doc:
            city_doc = db.cities.find_one({'name': {'$regex': f"^{re.escape(update_doc['city'])}$", '$options': 'i'}})
            if city_doc:
                update_doc['city_id'] = city_doc['_id']

        if 'screens' in data:
            update_doc['screens'] = int(data['screens'])

        if 'formats' in data:
            if isinstance(data['formats'], str):
                update_doc['formats'] = [f.strip() for f in data['formats'].split(',') if f.strip()]
            elif isinstance(data['formats'], list):
                update_doc['formats'] = data['formats']

        if 'active' in data:
            update_doc['active'] = bool(data['active'])

        db.theatres.update_one({'_id': t_oid}, {'$set': update_doc})
        return True, "Theatre updated successfully"

    def delete_theatre(self, theatre_id):
        t_oid = to_object_id(theatre_id)
        if not t_oid:
            return False, "Invalid theatre ID"
        db = get_db()
        db.theatres.delete_one({'_id': t_oid})
        db.shows.delete_many({'theatre_id': t_oid})
        return True, "Theatre deleted successfully"

theatre_service = TheatreService()

from bson import ObjectId
from datetime import datetime, date

def to_object_id(id_str):
    if not id_str:
        return None
    if isinstance(id_str, ObjectId):
        return id_str
    try:
        return ObjectId(str(id_str))
    except Exception:
        return None

def serialize_doc(doc):
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize_doc(item) for item in doc]
    if isinstance(doc, dict):
        serialized = {}
        for k, v in doc.items():
            if k == '_id' and isinstance(v, ObjectId):
                serialized['_id'] = str(v)
                serialized['id'] = str(v)
            elif isinstance(v, ObjectId):
                serialized[k] = str(v)
            elif isinstance(v, (datetime, date)):
                serialized[k] = v.isoformat()
            elif isinstance(v, dict):
                serialized[k] = serialize_doc(v)
            elif isinstance(v, list):
                serialized[k] = [serialize_doc(item) for item in v]
            else:
                serialized[k] = v
        return serialized
    return doc

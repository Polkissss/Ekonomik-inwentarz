from bson import ObjectId
from datetime import datetime
from app import mDB

# TODO: Add error handling to every model

class BaseModel():
    _collection = None

    @classmethod
    def FindBy_ID(cls, id):
        return cls._collection.find_one({"_id": ObjectId(id)})

    @classmethod
    def DeleteBy_ID(cls, id):
        return cls._collection.find_one_and_delete({"_id": ObjectId(id)})

    @classmethod
    def FindOne(cls, filter=None, projection=None):
        return cls._collection.find_one(filter or {}, projection)

    @classmethod
    def Find(cls, filter=None, projection=None):
        return cls._collection.find(filter or {}, projection)
from app.models.device import Device
from .base import BaseModel, mDB, ObjectId

class Rooms(BaseModel):
    _collection = mDB.db.rooms

    @classmethod
    def Edit(cls, _id, newKeeper):
        updatedRoom = cls._collection.find_one_and_update(
            {"_id": ObjectId(_id)},
            {"$set": {"keeper": newKeeper}},
            return_document=True
        )
        updatedRoom = dict(updatedRoom)
        updatedRoom.pop("_id")
        return Device.EditRoomKeeper(updatedRoom)
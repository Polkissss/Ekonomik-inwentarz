from .base import mDB, BaseModel, ObjectId

class Device(BaseModel):
    _collection = mDB.db.devices

    @classmethod
    def ValidateCreate(cls, docs):
        if docs["name"] == "":
            return False
        elif docs["ID"] == "":
            return False
        elif cls.FindByID(docs["ID"]):
            return False
        else:
            return True

    @classmethod
    def ValidateEdit(cls, docs):
        if docs["name"] == "":
            return False
        elif docs["ID"] == "":
            return False
        else:
            return True

    @classmethod
    def FindByID(cls, ID):
        return cls._collection.find_one({"ID": ID})

    @classmethod
    def Create(cls, docs):
        if cls.ValidateCreate(docs):
            return cls._collection.insert_one(docs)
        else:
            print("error")

    @classmethod
    def Edit(cls, _id ,docs):
        _id = ObjectId(_id)
        if cls.ValidateEdit(docs):
            cls._collection.find_one_and_update({"_id": _id}, {"$set": docs})
        else:
            print("error: Edycja urzadzenie nie powiodla sie")

    @classmethod
    def EditSpecName(cls, oldName, newName):
        return cls._collection.update_many(
            {"specs.Typ urządzenia": { "$exists": True}},
            {"$rename": {f"specs.{oldName}": f"specs.{newName}"}}
        )

    @classmethod
    def EditRoomKeeper(cls, room):
        return cls._collection.update_many(
            {"room.name": room["name"]},
            {"$set": {"room": room}}
        )

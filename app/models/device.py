from .base import mDB, BaseModel, ObjectId, ValidationError

class Device(BaseModel):
    _collection = mDB.db.devices

    @classmethod
    def ValidateCreate(cls, docs):
        if docs["name"] == "":
            raise ValidationError("Pole 'nazwa' jest wymagane.")
        elif docs["ID"] == "":
            raise ValidationError("Pole 'ID' jest wymagane.")
        elif cls.FindByID(docs["ID"]):
            raise ValidationError(f"Urządzenie o ID:  {docs["ID"]} istnieje już w bazie.")
        else:
            return True

    @classmethod
    def ValidateEdit(cls, docs):
        if docs["name"] == "":
            raise ValidationError("Pole 'nazwa' jest wymagane.")
        elif docs["ID"] == "":
            raise ValidationError("Pole 'ID' jest wymagane.")
        else:
            return True

    @classmethod
    def FindByID(cls, ID):
        return cls._collection.find_one({"ID": ID})

    @classmethod
    def Create(cls, docs):
        if cls.ValidateCreate(docs):
            return cls._collection.insert_one(docs)

    @classmethod
    def Edit(cls, _id ,docs):
        _id = ObjectId(_id)
        if cls.ValidateEdit(docs):
            cls._collection.find_one_and_update({"_id": _id}, {"$set": docs})

    @classmethod
    def EditSpecName(cls, oldName, newName):
        return cls._collection.update_many(
            {f"specs.{oldName}": { "$exists": True}},
            {"$rename": {f"specs.{oldName}": f"specs.{newName}"}}
        )

    @classmethod
    def EditRoomKeeper(cls, room):
        return cls._collection.update_many(
            {"room.name": room["name"]},
            {"$set": {"room": room}}
        )

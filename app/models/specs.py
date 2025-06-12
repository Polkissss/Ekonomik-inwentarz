from .base import BaseModel, mDB, ObjectId, ValidationError
from .device import Device

class Spec(BaseModel):
    _collection = mDB.db.specs

    @classmethod
    def Validate(cls, name="*", options="*"):
        if name == "":
            raise ValidationError("Pole 'nazwa' jest wymagane.")
        elif cls._collection.find_one({"name": name}):
            raise ValidationError(f"Nazwa: {name} już istnieje w bazie.")
        else:
            return True

    @classmethod
    def Create(cls, name, options):
        if cls.Validate(name, options):
            return cls._collection.insert_one({"name": name, "options": options})
        else:
            print("error")

    @classmethod
    def Edit(cls, _id, newName, options):
        if cls.Validate(newName, options):
            oldName = cls._collection.find_one({"_id": ObjectId(_id)})["name"]
            Device.EditSpecName(oldName, newName)
            return cls._collection.find_one_and_update({"_id": ObjectId(_id)}, {"$set": {"name": newName, "options": options}})
        else:
            print("error")

    @classmethod
    def EditName(cls, _id, newName):
        if cls.Validate(newName):
            oldName = cls._collection.find_one({"_id": ObjectId(_id)})["name"]
            Device.EditSpecName(oldName, newName)
            return cls._collection.find_one_and_update({"_id": ObjectId(_id)}, {"$set": {"name": newName}})
        else:
            print("error")

    @classmethod
    def EditOptions(cls, _id, options):
        if cls.Validate(options=options):
            return cls._collection.find_one_and_update({"_id": ObjectId(_id)}, {"$set": {"options": options}})
        else:
            print("error")
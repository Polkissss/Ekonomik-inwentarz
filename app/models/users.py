from .base import BaseModel, mDB, datetime

class Users(BaseModel):
    _collection = mDB.db.users

    @classmethod
    def Create(cls, name, permission=False, lastLogin=datetime.now()):
        if not cls._collection.find_one({"name": name}):
            return cls._collection.insert_one({
                "name": name,
                "last_login": lastLogin,
                "permission": permission,
                "last_action": "Brak",
                "action_item": "Brak"
            })
        else:
            print("error")

    @classmethod
    def EditLastLogin(cls, name):
        return cls._collection.find_one_and_update({"name": name}, {"$set": {"last_login": datetime.now()}})

    @classmethod
    def EditLastAction(cls, name, type, affectedID):
        return cls._collection.find_one_and_update({"name": name}, {"$set": {"last_action": datetime.now(), "action_item": f"{type}: {affectedID}"}})

    @classmethod
    def EditPrviledges(cls, name, state):
        return  cls._collection.find_one_and_update({"name": name}, {"$set": {"permission": state}})

    @classmethod
    def DeleteByName(cls, name):
        return cls._collection.delete_one({"name": name})
from datetime import datetime
from .base import BaseModel, mDB

class Settings(BaseModel):
    _collection = mDB.db.settings

    # Update method to settings collection for user filters.
    # If document doesn't exist it creates it. If state is empty for some reason force enable
    @classmethod
    def UpdateFilter(cls, state=False):
        if state == True or state == False:
            return  cls._collection.find_one_and_update(
                {"name": "user_filtration"},
                {"$set":
                    {
                    "state": state,
                    "last_updated": datetime.now()
                    }
                }, 
                upsert=True
            )

    @classmethod
    def GetFilterState(cls):
        filter = cls._collection.find_one({"name": "user_filtration"})
        return filter["state"]


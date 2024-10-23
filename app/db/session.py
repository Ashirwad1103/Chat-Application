 
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
import os
from ..models.collections import Collections
from ..configs.app_config import Settings
from fastapi import Depends
from ..utils.decorators import singleton



# class MongoDBClient:
#     _instance = None

#     def __new__(cls, uri: str, database_name: str):
#         if cls._instance is None:
#             cls._instance = super(MongoDBClient, cls).__new__(cls)
#             cls._instance.client = AsyncIOMotorClient(uri)
#             cls._instance.db = cls._instance.client[database_name]
#         return cls._instance
    
#     def get_collection(self, collectionName: Collections) -> AsyncIOMotorCollection: 
#         return self.db[collectionName]


#NOTE - This class should be singleton because AsyncIOMotorClient manages a connection pool internally, so creating multiple instance is resource wastage.
@singleton
class MongoDBClient:    
    def __init__(self, uri: str, database_name: str) -> None:
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database_name]
    
    def get_collection(self, collectionName: Collections) -> AsyncIOMotorCollection: 
        return self.db[collectionName]


def get_mongo_client(settings: Settings = Depends(Settings)) -> MongoDBClient:
    uri = settings.MONGO_HOST
    database_name = settings.MONGO_DB_NAME
    # print("Settings loaded")
    mongo_client = MongoDBClient(uri=uri, database_name=database_name)
    # print(f"{mongo_client=}")
    return mongo_client
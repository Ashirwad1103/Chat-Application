from fastapi import HTTPException, status, Depends
from ..models.request_models import Group, JoinGroup
from ..models.collections import Collections
from ..db.session import MongoDBClient, get_mongo_client
from uuid import uuid4

from icecream import ic
ic.configureOutput(includeContext=True)


class GroupService:
    def __init__(self, mongo_client: MongoDBClient) -> None:
        self.mongo_client = mongo_client
        self.group_collection = self.mongo_client.get_collection(collectionName=Collections.GROUPS)
        self.group_user_collection = self.mongo_client.get_collection(collectionName=Collections.GROUP_USER)


    async def get_group_by_id(self, group_id: str) -> dict: 
        db_group = await self.group_collection.find_one(filter={
            "id": group_id
        })
        return db_group
    
    async def raise_on_group_not_found(self, group_id): 
        db_group = await self.get_group_by_id(group_id=group_id)
        if not db_group: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group with this id not found")


    async def create_group(self, group: Group):

        if not group.name: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Name field is required for creating group")

        group_id = str(uuid4())
        group_doc = {
            'id': group_id,
            'name': group.name,
        }

        await self.group_collection.insert_one(document=group_doc)
        return {"group_id": group_id}

    async def join_group(self, join_group_request: JoinGroup): 
        
        db_group_user = await self.group_user_collection.find_one(filter={
            "group_id": join_group_request.group_id,
            "user_email": join_group_request.user_email
        })

        ic(db_group_user)

        if db_group_user: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="User already a member of this group!")

        group_user_doc = {
            "group_id": join_group_request.group_id, 
            "user_email": join_group_request.user_email
        }
    
        await self.group_user_collection.insert_one(document=group_user_doc)
        return 

    async def get_group_members(self, group_id: str):
        db_group_users = await self.group_user_collection.find({
            "group_id": group_id
        }, {"_id": 0}).to_list(length=None)

        ic(db_group_users)

        return db_group_users

        
        
def get_group_service(mongo_client: MongoDBClient = Depends(get_mongo_client)):
    return GroupService(mongo_client=mongo_client)

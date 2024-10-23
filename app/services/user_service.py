from fastapi import HTTPException, status, Depends
from ..models.request_models import User
from ..models.collections import Collections
from ..db.session import MongoDBClient, get_mongo_client
from .password_service import PasswordService
from .jwt_service import JwtService
from typing import List
from pymongo.errors import PyMongoError


class UserService:
    def __init__(self, mongo_client: MongoDBClient) -> None:
        self.mongo_client = mongo_client
        self.user_collection = self.mongo_client.get_collection(collectionName=Collections.USERS)
        print("User Service init success")


    async def get_user_by_email(self, email: str) -> dict: 
        try:
            db_user = await self.user_collection.find_one(filter={
                "email": email
            })
        except PyMongoError as e: 
            print(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database query failed")
        return db_user

    async def ensure_user_exits(self, email: str) -> None: 
        db_user = await self.get_user_by_email(email=email)
        if db_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    async def ensure_user_not_found(self, email: str) -> None:
        db_user = await self.get_user_by_email(email=email)
        if not db_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email not found")

    async def signup(self, user: User, password_service: PasswordService):

        if not user.name: 
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Name field is required for signup")

        user.password = password_service.hash_password(password=user.password)

        user_doc = {
            'email': user.email,
            'name': user.name,
            'password': user.password
        }

        try:
            await self.user_collection.insert_one(document=user_doc)
        except PyMongoError as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database query failed")
    
    async def login(self, user: User, password_service: PasswordService, jwt_service: JwtService):
        db_user = await self.get_user_by_email(user.email)
        
        if not password_service.verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
        
        payload = {
            "email": db_user.get("email"), 
        }
        token = jwt_service.encode_jwt(payload=payload)
        return token
    
    async def get_user_records(self, user_emails: List[str]): 
        query = {"email": {"$in": user_emails}}
        try: 
            db_user_records = await self.user_collection.find(query).to_list(length=None)
        except PyMongoError as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database query failed")        
        return db_user_records
        


def get_user_service(mongo_client: MongoDBClient = Depends(get_mongo_client)) -> UserService:
    return UserService(mongo_client=mongo_client)
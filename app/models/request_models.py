from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class User(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    password: str


class Group(BaseModel):
    name: str

class JoinGroup(BaseModel):
    group_id: str
    user_email: EmailStr
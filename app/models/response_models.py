# app/models/jwt_payload.py

from pydantic import BaseModel
from datetime import datetime
from typing import List

class JWTPayload(BaseModel):
    email: str
    exp: datetime

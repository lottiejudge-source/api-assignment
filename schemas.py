from pydantic import BaseModel, Field
from typing import List
from uuid import UUID 

class CoinCreate(BaseModel):
    coin_name: str
    coin_complete: bool = False
    duty_ids: List[UUID]

class UserCreate(BaseModel):
    user_name: str = Field(..., pattern=r"^[a-zA-Z0-9_]+$")
    user_password: str = Field(..., min_length = 8)
    role: str = Field(..., pattern="^(authorised|admin)+$")

class UserLogin(BaseModel):
    user_name: str = Field(..., pattern=r"^[a-zA-Z0-9_]+$")
    user_password: str = Field(..., min_length=8)
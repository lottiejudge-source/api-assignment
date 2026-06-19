from pydantic import BaseModel 
from typing import List
from uuid import UUID 

class CoinCreate(BaseModel):
    coin_name: str
    coin_complete: bool = False
    duty_ids: List[UUID]
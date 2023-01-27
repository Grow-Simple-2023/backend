from typing import List
from pydantic import BaseModel

class DistributeModel(BaseModel):
    item_ids: List[str]
    rider_phone_nos: List[str]
    
class ItemStatusModel(BaseModel):
    item_id: str
    status: int
    OTP: int
    phone_no: str

from typing import List
from pydantic import BaseModel

class DistributeModel(BaseModel):
    item_ids: List[str]
    rider_phone_nos: List[str]
    
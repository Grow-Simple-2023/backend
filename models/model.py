from typing import List
from pydantic import BaseModel
from enum import Enum

class ModifyRoute(BaseModel):
    rider_id: str
    item_ids_in_order: List[str]

class DistributeModel(BaseModel):
    item_ids: List[str]
    rider_phone_nos: List[str]
    
class ItemStatusModel(BaseModel):
    item_id: str
    status: int
    OTP: int

class RouteEndModel(BaseModel):
    route_otp: int

class Role(str, Enum):
    admin = "ADMIN"
    rider = "RIDER"
    
class Register(BaseModel):
    phone_no: str
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    phone_no: str
    password: str
    role: Role
    
class Token(BaseModel):
    access_token: str
    token_type: str

class Login(BaseModel):
    phone_no: str
    password: str
    
class Location(BaseModel):
    latitude: float
    longitude: float
    timestamp: int

class ItemDimData(BaseModel):
    item_id: str
    length: float
    breadth: float
    height: float
    weight: float
from typing import List
from pydantic import BaseModel
from enum import Enum

class ModifyRoute(BaseModel):
    """ model used for modifying route """
    rider_id: str
    item_ids_in_order: List[str]

class DistributeModel(BaseModel):
    """model used for DistributeModel"""
    item_ids: List[str]
    rider_phone_nos: List[str]
    
class ItemStatusModel(BaseModel):
    """ model used for updating item status like cancel and delivered """
    item_id: str
    status: int
    OTP: int

class RouteEndModel(BaseModel):
    """ model used for ending route """
    route_otp: int

class Role(str, Enum):
    """model used for role of user"""
    admin = "ADMIN"
    rider = "RIDER"
    
class Register(BaseModel):
    """model used for register user"""
    phone_no: str
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    phone_no: str
    password: str
    role: Role
    
class Token(BaseModel):
    """ model used for jwttoken """
    access_token: str
    token_type: str

class Login(BaseModel):
    """ model used for Login user """
    phone_no: str
    password: str
    
class Location(BaseModel):
    """ model used for location """
    latitude: float
    longitude: float
    timestamp: int

class ItemDimData(BaseModel):
    """ model used for item dimensions """
    item_id: str
    length: float
    breadth: float
    height: float
    weight: float
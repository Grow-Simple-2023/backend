from enum import Enum
from pydantic import BaseModel

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
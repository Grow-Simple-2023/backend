
from config.db_config import db
from models.model import *
from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException, status
from services.auth import check_user_exists, add_new_user, verify_credentials, create_token

router = APIRouter()


@router.get("/")
async def generic_home():
    data = {
        "message": "Welcome to Grow-Simplee API",
        "collections": db.list_collection_names()
    }
    return data


@router.post("/register")
async def register(register: Register):
    if register.password!=register.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if len(register.password)<8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password length must be atleast 8")
    token = Token(**{"access_token": "encoded", "token_type": "Bearer"})
    if(not register.phone_no.isnumeric() or len(register.phone_no) != 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide correct phone number")
    check_user_exists(register.phone_no)
    user = add_new_user(phone_no=register.phone_no, first_name=register.first_name, last_name=register.last_name, password=register.password, role=register.role)
    token = create_token(phone_no=user["phone_no"], role=user["role"])
    return {"user": user, 
            "auth": token} 

@router.post("/login")
async def login(login: Login):
    if(not login.phone_no.isnumeric() or len(login.phone_no) != 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide correct phone number")
    user = verify_credentials(phone_no=login.phone_no, password=login.password)
    token = create_token(phone_no=user["phone_no"], role=user["role"])
    return token
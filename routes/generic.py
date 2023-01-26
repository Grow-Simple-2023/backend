
from config.db_config import db
from models.model import *
from dotenv import load_dotenv
from fastapi import APIRouter, Request, HTTPException, status
from services.auth import check_user_exists, add_new_user

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
    token = Token(**{"access_token": "encoded", "token_type": "Bearer"})
    if(not register.phone_no.isnumeric() or len(register.phone_no) != 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide correct phone number")
    check_user_exists(register.phone_no)
    user = add_new_user(phone_no=register.phone_no, first_name=register.first_name, last_name=register.last_name, password=register.password, role=register.role)
    print(user)
    return user 

@router.post("/login")
async def login():
    return {"data":"data"}
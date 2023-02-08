
from models.model import *
from services.auth import *
from services.anomaly_detect import *
from dotenv import load_dotenv
from config.db_config import db
from fastapi import APIRouter, Request, HTTPException, status, Depends

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
    """ endpoint used for registering a new user """
    if register.password != register.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")
    if len(register.password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password length must be atleast 8")
    token = Token(**{"access_token": "encoded", "token_type": "Bearer"})
    if (not register.phone_no.isnumeric() or len(register.phone_no) != 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provide correct phone number")
    check_user_exists(register.phone_no)
    user = add_new_user(phone_no=register.phone_no, first_name=register.first_name,
                        last_name=register.last_name, password=register.password, role=register.role)
    token = create_token(phone_no=user["phone_no"], role=user["role"])
    return {"user": user,
            "auth": token}


@router.post("/login")
async def login(login: Login):
    """ endpoint used for logging in a user """
    if (not login.phone_no.isnumeric() or len(login.phone_no) != 10):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Provide correct phone number")
    user = verify_credentials(phone_no=login.phone_no, password=login.password)
    token = create_token(phone_no=user["phone_no"], role=user["role"])
    return {"token": token, "role": user["role"]}


@router.get("/decode-token")
async def decode_token(load: str = Depends(decode_jwt)):
    """ endpoint used for decoding a token """
    return load


@router.post("/add-item-details")
async def add_item_details(item_dim_data: List[ItemDimData]):
    """ endpoint used for adding item details """
    item_ids = [item.item_id for item in item_dim_data]
    item_dims = [[item.length, item.breadth, item.height, item.weight]
                 for item in item_dim_data]
    rejected_indices = anomaly_detect(item_dims)
    rejected_ids = [item_ids[x] for x in rejected_indices]
    for index, id in enumerate(item_ids):
        if id in rejected_ids:
            continue
        db.item.update_one(
            {"id": id}, {"$set": {"description.length": item_dim_data[index].length,
                                  "description.breadth": item_dim_data[index].breadth,
                                  "description.height": item_dim_data[index].height,
                                  "description.weight": item_dim_data[index].weight}})
    
    db.item.update_many({"id": {"$in": rejected_ids}}, {"$set": {"control.is_cancelled": True}})
    return {"rejected_ids": rejected_ids}

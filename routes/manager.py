from fastapi import APIRouter
from config.db_config import db

router = APIRouter()


@router.get("/")
async def manager_home():
    return {"message": "Welcome to Grow-Simplee Manager API"}

@router.get("/items/{item_id}")
async def get_item(item_id: str):
    return db.item.find_one({"id": item_id}, {"_id": 0})

@router.get("/riders")
async def get_rider():
    documents = db.user.find({"role": "RIDER"}, {"_id": 0})
    return [document for document in documents]

@router.get("/riders/{rider_no}")
async def get_rider(rider_no: str):
    return db.user.find_one({"phone_no": rider_no, "role": "RIDER"}, {"_id": 0})
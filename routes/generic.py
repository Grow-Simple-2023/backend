from fastapi import APIRouter
from config.db_config import db

router = APIRouter()


@router.get("/")
async def generic_home():
    data = {
        "message": "Welcome to Grow-Simplee API",
        "collections": db.list_collection_names()
    }
    return data
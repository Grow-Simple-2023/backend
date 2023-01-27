from fastapi import APIRouter, HTTPException
from config.db_config import db


router = APIRouter()


@router.get("/")
async def rider_home():
    return {"message": "Welcome to Grow-Simplee Rider API"}

@router.get("/route/{phone_no}")
def get_route_by_number(phone_no: str):
    route = db.route.find_one({"rider_id": phone_no}, {"_id": 0})
    if not route: raise HTTPException(status_code=404, detail=f"Rider not assigned to a route: {phone_no}")
    return route
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

@router.delete("/end-route")
async def end_route(route_end_model: RouteEndModel):
    route_info = db.route.find_one({"rider_id": route_end_model.rider_id, 
                                    "route_otp": route_end_model.route_otp}, {"_id": 0})
    if not route_info:
        raise HTTPException(status_code=404, detail=f"Wrong OTP / Item not Assigned: {route_end_model.rider_id}")
    db.route.delete_one({"rider_id": route_end_model.rider_id})
    for item in route_info["items_in_order"]:
        db.item.update_one({"id": item["id"]}, {"$set": {"control.is_assigned": False,
                                                        "control.is_fulfilled": False,
                                                        "conrtol.is_cancelled": False}})
    return db.route.find_one({"rider_id": route_end_model.rider_id}, {"_id": 0})
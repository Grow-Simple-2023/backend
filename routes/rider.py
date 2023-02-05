from services.auth import *
from datetime import datetime
from config.db_config import db
from fastapi import APIRouter, HTTPException, Depends
from models.model import *


router = APIRouter()


@router.get("/")
async def rider_home(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    return {"message": "Welcome to Grow-Simplee Rider API"}


@router.get("/route/{phone_no}")
async def get_route_by_number(phone_no: str, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    route = db.route.find_one({"rider_id": phone_no}, {"_id": 0})
    if not route:
        raise HTTPException(
            status_code=404, detail=f"Rider not assigned to a route: {phone_no}")
    return {"route": route}


@router.post("/item-status-update")
async def item_status_update(item_status: ItemStatusModel, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    rider = db.route.find_one(
        {"items_in_order.id": item_status.item_id, "rider_id": user_data.phone_no}, {"_id": 0})
    if not rider:
        raise HTTPException(
            status_code=404, detail="Item not assigned to " + str(user_data.phone_no) + " rider")

    item = db.item.find_one({"id": item_status.item_id}, {"_id": 0, "OTP": 1})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if item["OTP"] != item_status.OTP:
        raise HTTPException(status_code=404, detail="OTP does not match")

    if item_status.status not in [0, 1]:
        raise HTTPException(status_code=404, detail="Status error")

    control = {"is_fulfilled": item_status.status == 1,
               "is_cancelled": item_status.status == 0, "is_assigned": False}
    db.item.update_one({"id": item_status.item_id}, {
                       "$set": {"control": control, "delivered_on": str(datetime.now())}})

    db.route.update_one({"rider_id": user_data.phone_no},
                        {"$pull": {"items_in_order": {"id": item_status.item_id}},
                         "$set": {"last_modified": str(datetime.now())}})

    item = db.item.find_one({"id": item_status.item_id}, {"_id": 0})
    return {"updated_item": item} if item_status.status == 0 else item


@router.post("/modify-route")
async def modify_route(modify_route: ModifyRoute, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    rider_id, item_ids_in_order = modify_route.rider_id, modify_route.item_ids_in_order
    if (user_data["role"] == "RIDER"):
        if (rider_id != user_data["phone_no"]):
            raise HTTPException(
                status_code=404, detail="You are not authorized to modify this route")
    existing_route = db.route.find_one({"rider_id": rider_id}, {"_id": 0})
    if not existing_route:
        raise HTTPException(
            status_code=404, detail=f"Route not found: {rider_id}")
    existing_order = existing_route["items_in_order"]
    existing_order_dict = {item["id"]: item for item in existing_order}

    try:
        new_order = [existing_order_dict[id] for id in item_ids_in_order]
        assert len(new_order) == len(existing_order)
    except:
        raise HTTPException(
            status_code=404, detail=f"Invalid order")
    db.route.update_one({"rider_id": rider_id}, {
                        "$set": {"items_in_order": new_order, "last_modified": str(datetime.now())}})
    return {"items_in_route": db.route.find_one({"rider_id": rider_id}, {"_id": 0})}


@router.get("/is-route-modified-after/{route_id}")
async def is_route_modified_after(route_id: str, last_modified: str, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    if (user_data["role"] == "RIDER" and route_id != user_data["phone_no"]):
        raise HTTPException(
            status_code=404, detail="You are not authorized to modify this route")
    existing_route = db.route.find_one(
        {"rider_id": route_id}, {"_id": 0, "last_modified": 1})
    if not existing_route:
        raise HTTPException(
            status_code=404, detail=f"Route not found: {route_id}")
    return {"is_modified": existing_route["last_modified"] > last_modified}


@router.post("/send-self-location")
async def send_self_location(location: Location, user_data=Depends(decode_jwt)):
    check_role(user_data, ["RIDER"])
    phone_no = check_role["phone_no"]
    route_info = db.route.find_one({"rider_id": phone_no})
    if not route_info:
        raise HTTPException(
            status_code=404, detail=f"Route not found: {phone_no}")

    doc = {
        "latitude": location.latitude,
        "longitiude": location.longitiude,
        "time": location.timestamp
    }
    db.route.update_one({"rider_id": phone_no}, {
                        "$push": {"rider_location": doc}})
    return {"message": "Location Updated Successfully"}

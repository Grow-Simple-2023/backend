from fastapi import APIRouter, HTTPException, Depends
from config.db_config import db
from models.model import ItemStatusModel, RouteEndModel
from datetime import datetime
from services.auth import *


router = APIRouter()


@router.get("/")
async def rider_home(user_data = Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    return {"message": "Welcome to Grow-Simplee Rider API"}

@router.get("/route/{phone_no}")
async def get_route_by_number(phone_no: str, user_data = Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    route = db.route.find_one({"rider_id": phone_no}, {"_id": 0})
    if not route: raise HTTPException(status_code=404, detail=f"Rider not assigned to a route: {phone_no}")
    return route

@router.post("/item-status-update")
async def item_status_update(item_status: ItemStatusModel, user_data = Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    rider_with_item_details = db.route.find_one({"items_in_order.id": item_status.item_id,
                                                 "rider_id":user_data.phone_no}, {"_id": 0})
    if not rider_with_item_details:
         raise HTTPException(status_code=404, detail="Item not assigned to " + str(user_data.phone_no)+" rider")
    OTP = db.item.find_one({"id": item_status.item_id}, {"_id": 0,"OTP":1})
    if(OTP["OTP"] == item_status.OTP):
        if(item_status.status==1):
            db.item.update_one({"id": item_status.item_id}, {"$set": {"control.is_fulfilled": True,
                                                                      "control.is_assigned": False,
                                                                      "control.is_cancelled": False,
                                                                      "delivered_on": str(datetime.now())}})
            db.route.update_one({"rider_id": user_data.phone_no}, {"$pull": {"items_in_order": 
                                                                               {"id": item_status.item_id}}})
            item = db.item.find_one({"id": item_status.item_id}, {"_id": 0})
            return item
        elif item_status.status==0:
            db.item.update_one({"id": item_status.item_id}, {"$set": {"control.is_cancelled": True,"control.is_fulfilled": False,"control.is_pickup": False,"control.is_assigned":False,"control.is_delivery":False}})
            db.route.update_one({"rider_id": user_data.phone_no}, {"$pull": {"items_in_order": 
                                                                               {"id": item_status.item_id}}})
            item = db.item.find_one({"id": item_status.item_id}, {"_id": 0})
            return item
        else:
            raise HTTPException(status_code=404, detail="Status error")
    else:
        raise HTTPException(status_code=404, detail="OTP does not match")

@router.delete("/end-route")
async def end_route(route_end_model: RouteEndModel, user_data = Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    route_info = db.route.find_one({"rider_id": route_end_model.rider_phone_no, 
                                    "route_otp": route_end_model.route_otp}, {"_id": 0})
    if not route_info:
        raise HTTPException(status_code=404, detail=f"Wrong OTP / Item not Assigned: {route_end_model.rider_phone_no}")
    db.route.delete_one({"rider_id": route_end_model.rider_phone_no})
    for item in route_info["items_in_order"]:
        db.item.update_one({"id": item["id"]}, {"$set": {"control.is_assigned": False,
                                                        "control.is_fulfilled": False,
                                                        "conrtol.is_cancelled": False}})
    return route_info

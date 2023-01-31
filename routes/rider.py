from services.auth import *
from datetime import datetime
from config.db_config import db
from fastapi import APIRouter, HTTPException, Depends
from models.model import ItemStatusModel, RouteEndModel


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
    return {"route": route}

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
            return {"updated_item": item}
        else:
            raise HTTPException(status_code=404, detail="Status error")
    else:
        raise HTTPException(status_code=404, detail="OTP does not match")

@router.delete("/end-route")
async def end_route(route_end_model: RouteEndModel, user_data = Depends(decode_jwt)):
    check_role(user_data, ["ADMIN", "RIDER"])
    phone_no = user_data["phone_no"]
    route_info = db.route.find_one({"rider_id": phone_no, 
                                    "route_otp": route_end_model.route_otp}, {"_id": 0})
    if not route_info:
        raise HTTPException(status_code=404, detail=f"Wrong OTP / Item not Assigned: {phone_no}")
    db.route.delete_one({"rider_id": phone_no})
    for item in route_info["items_in_order"]:
        db.item.update_one({"id": item["id"]}, {"$set": {"control.is_assigned": False,
                                                        "control.is_fulfilled": False,
                                                        "conrtol.is_cancelled": False}})
    return {"deleted_route": route_info}

@router.put("/modify-route")
async def modify_route(rider_id: str, item_ids_in_order: List[str], user_data = Depends(decode_jwt(request))):
    check_role(user_data, ["ADMIN", "RIDER"])
    if(role=="RIDER"):
        if(rider_id != user_data["phone_no"]):
            raise HTTPException(status_code=404, detail="You are not authorized to modify this route")
    existing_route = db.route.find_one({"rider_id": rider_id}, {"_id": 0})
    if not existing_route:
        raise HTTPException(status_code=404, detail=f"Route not found: {rider_id}")
    existing_order = existing_route["items_in_order"]
    new_order = []
    for order in item_ids_in_order:
        for item in existing_order:
            if item["id"] == order:
                new_order.append(item)
    try:
        assert len(new_order) == len(existing_order)
    except:
        raise HTTPException(status_code=404, detail=f"Invalid order: {rider_id}")
    db.route.update_one({"rider_id": rider_id}, {"$set": {"items_in_order": new_order}})
    return {"items_in_route": db.route.find_one({"rider_id": rider_id}, {"_id": 0})}
    

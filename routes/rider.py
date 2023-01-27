from fastapi import APIRouter,HTTPException, Request as HTTPRequest
from config.db_config import db
from models.model import ItemStatusModel
from datetime import datetime
router = APIRouter()


@router.get("/")
async def rider_home():
    return {"message": "Welcome to Grow-Simplee Rider API"}

@router.get("/route/{phone_no}")
async def get_route_by_number(phone_no: str):
    route = db.route.find_one({"rider_id": phone_no}, {"_id": 0})
    if not route: raise HTTPException(status_code=404, detail="Route does not exist")
    return route

@router.post("/item-status-update")
async def item_status_update(item_status: ItemStatusModel):
    rider_with_item_details = db.route.find_one({"items_in_order.id": item_status.item_id,
                                                 "rider_id":item_status.phone_no}, {"_id": 0})
    if not rider_with_item_details:
         raise HTTPException(status_code=404, detail="Item not assigned to " + str(item_status.phone_no)+" rider")
    OTP = db.item.find_one({"id": item_status.item_id}, {"_id": 0,"OTP":1})
    if(OTP["OTP"] == item_status.OTP):
        if(item_status.status==1):
            db.item.update_one({"id": item_status.item_id}, {"$set": {"control.is_fulfilled": True,
                                                                      "delivered_on": str(datetime.now())}})
            db.route.update_one({"rider_id": item_status.phone_no}, {"$pull": {"items_in_order": 
                                                                               {"id": item_status.item_id}}})
            item = db.item.find_one({"id": item_status.item_id}, {"_id": 0})
            return item
        elif item_status.status==0:
            db.item.update_one({"id": item_status.item_id}, {"$set": {"control.is_cancelled": True,"control.is_fulfilled": False,"control.is_pickup": False,"control.is_assigned":False,"control.is_delivery":False}})
            db.route.update_one({"rider_id": item_status.phone_no}, {"$pull": {"items_in_order": 
                                                                               {"id": item_status.item_id}}})
            item = db.item.find_one({"id": item_status.item_id}, {"_id": 0})
            return item
        else:
            raise HTTPException(status_code=404, detail="Status error")
    else:
        raise HTTPException(status_code=404, detail="OTP does not match")
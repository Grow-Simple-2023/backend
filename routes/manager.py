from fastapi import APIRouter
from config.db_config import db
from datetime import datetime
import json

router = APIRouter()


@router.get("/")
async def manager_home():
    return {"message": "Welcome to Grow-Simplee Manager API"}

@router.get("/OTD-percentage")
async def on_time_delivery_percentage():
    no_of_successful_deleveries = len(list(db.item.find({"EDD":{"$lte":str(datetime.now())},
                                                      "control.is_fulfilled":True,
                                                      "$expr":{"$lte":["$delivered_on","$EDD"]}})))
    total_deliveries_to_be_done = len(list(db.item.find({"EDD":{"$lte":str(datetime.now())}})))

    percentage_of_successful_deliveries = (no_of_successful_deleveries/total_deliveries_to_be_done)*100
    return {"percentage": percentage_of_successful_deliveries}

@router.get("/curr-items-in-del")
async def current_items_in_delivery():
    items_in_delivery = list(db.item.find({"control.is_assigned":True,"control.is_fulfilled":False}, {"_id": 0}))
    return {"items_in_delivery": items_in_delivery} 
                                                
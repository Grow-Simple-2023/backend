from fastapi import APIRouter, HTTPException
from config.db_config import db
from datetime import datetime
import json
from models.model import DistributeModel
from services.Clustering import Clustering
from services.TSP import TSP
from time import time

router = APIRouter()


@router.get("/")
async def manager_home():
    return {"message": "Welcome to Grow-Simplee Manager API"}

@router.get("/OTD-percentage")
async def on_time_delivery_percentage():
    no_of_successful_deleveries = len(list(db.item.find({"EDD":{"$lte":str(datetime.now())},
                                                      "control.is_fulfilled":True,
                                                      "$expr":{"$lte":["$delivered_on","$EDD"]},
                                                      "control.is_cancelled": False})))
    
    total_deliveries_to_be_done = len(list(db.item.find({"EDD":{"$lte":str(datetime.now())}, 
                                                         "control.is_cancelled": False})))

    percentage_of_successful_deliveries = (no_of_successful_deleveries/total_deliveries_to_be_done)*100
    return {"percentage": percentage_of_successful_deliveries}

@router.get("/items-in-delivery")
async def current_items_in_delivery():
    items_in_delivery = list(db.item.find({"control.is_assigned":True,"control.is_fulfilled":False}, {"_id": 0}))
    return {"items_in_delivery": items_in_delivery} 
                                                
@router.get("/items/{item_id}")
async def get_item(item_id: str):
    return db.item.find_one({"id": item_id}, {"_id": 0})

@router.get("/unassigned-items")
async def unassigned_items():
    documents = list(db.item.find({"control.is_fulfilled": False, 
                                   "control.is_assigned": False, 
                                   "control.is_cancelled": False}, {"_id": 0}))
    print(documents)
    return {"unassigned_items": documents}


@router.get("/riders")
async def get_rider():
    documents = list(db.user.find({"role": "RIDER"}, {"_id": 0}))
    return {"riders": documents}

@router.get("/riders/{rider_no}")
async def get_rider(rider_no: str):
    return db.user.find_one({"phone_no": rider_no, "role": "RIDER"}, {"_id": 0})

@router.post("/distribute")
async def distribute_items(distribution_info: DistributeModel):
    start = time()
    rider_vol = []
    for phone_no in distribution_info.rider_phone_nos:
        try:
            assert db.user.find_one({"phone_no": phone_no, "role": "RIDER"})
            rider_vol.append(400000)
        except:
            raise HTTPException(status_code=404, detail=f"Phone number does not belong to a rider: {phone_no}")
    
    no_riders = len(distribution_info.rider_phone_nos)
    item_dims, item_lat_long = [], []
    for item_id in distribution_info.item_ids:
        try:
            item_info = db.item.find_one({"id": item_id, "control.is_assigned": False, 
                                          "control.is_fulfilled": False,
                                          "control.is_cancelled": False}, {"description.weight": 0})
            assert item_info
            item_dims.append(tuple(item_info["description"].values()))
            item_lat_long.append(tuple(item_info["location"].values()))
        except Exception as E:
            raise HTTPException(status_code=404, detail=f"Item does not exist or is already assigned: {item_id}")
    
    cluster = Clustering(item_dims, item_lat_long, no_riders, rider_vol)
    distribution = cluster.distribute()
    all_routes = []
    total_cost = 0
    for cluster in distribution:
        temp_lat_long = []
        for id in cluster: temp_lat_long.append(item_lat_long[id])
        tsp = TSP(temp_lat_long)
        temp_path, temp_path_cost, _ = tsp.approximation_1_5()
        for i in range(3):
            temp_path, temp_path_cost, _ = tsp.two_edge_switch(2, temp_path)
            temp_path, temp_path_cost, _ = tsp.three_edge_switch(2, temp_path)
            temp_path, temp_path_cost, _ = tsp.two_edge_switch(2, temp_path)
        temp_path, temp_path_cost, _ = tsp.node_edge_insert(2, temp_path) 
        # temp_path, temp_path_cost, _ = tsp.perfect()
        total_cost += temp_path_cost
        path = []
        for node in temp_path: path.append(cluster[node])
        all_routes.append(path[:])
        
    return {"distribution": distribution, "routes": all_routes, "time_taken": time()-start, "total_cost": total_cost}
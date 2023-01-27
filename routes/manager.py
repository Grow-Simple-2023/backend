from fastapi import APIRouter, HTTPException
from config.db_config import db
from datetime import datetime
import json
from models.model import DistributeModel
from services.Clustering import Clustering
from services.TSP import TSP, road_distance
from time import time
import random

router = APIRouter()


@router.get("/")
async def manager_home():
    return {"message": "Welcome to Grow-Simplee Manager API"}

# to calculate on time delivery percentage
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

# items in delivery
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

@router.get("/unassigned-riders")
async def get_unassigned_rider():
    a_riders = []
    assigned_riders = list(db.route.find({}, {"_id": 0}))
    for rider in assigned_riders: a_riders.append(rider["rider_id"])
    documents = list(db.rider.find({"id": {"$nin": assigned_riders}}, {"_id": 0}))
    return {"unassigned_riders": documents}

@router.get("/riders/{rider_no}")
async def get_rider(rider_no: str):
    return db.user.find_one({"phone_no": rider_no, "role": "RIDER"}, {"_id": 0})

@router.post("/distribute")
async def distribute_items(distribution_info: DistributeModel):
    start = time()
    rider_vol = []
    hub_lat_long = db.item.find_one({"id": "Hub"})["location"]
    hub_location = tuple(hub_lat_long.values())
    for phone_no in distribution_info.rider_phone_nos:
        try:
            assert db.user.find_one({"phone_no": phone_no, "role": "RIDER"})
            rider_vol.append(400000)
        except:
            raise HTTPException(status_code=404, detail=f"Phone number does not belong to a rider: {phone_no}")
    
    no_riders = len(distribution_info.rider_phone_nos)
    item_dims, item_lat_long, EDD = [], [], []
    for item_id in distribution_info.item_ids:
        try:
            item_info = db.item.find_one({"id": item_id, "control.is_assigned": False, 
                                          "control.is_fulfilled": False,
                                          "control.is_cancelled": False}, {"description.weight": 0})
            assert item_info
            item_dims.append(tuple(item_info["description"].values()))
            item_lat_long.append(tuple(item_info["location"].values()))
            EDD.append(item_info["EDD"])
        except Exception as E:
            raise HTTPException(status_code=404, detail=f"Item does not exist or is already assigned: {item_id}")
    
    cluster = Clustering(item_dims, item_lat_long, no_riders, rider_vol, EDD)
    distribution = cluster.distribute()
    
    
    for i in range(len(distribution)):
        for j in range(len(distribution[i])):
            distribution[i][j]+=1
    all_routes = []
    total_cost = 0
    for cluster in distribution:
        temp_lat_long = [hub_location]
        for id in cluster: temp_lat_long.append(item_lat_long[id-1])
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
        for node in temp_path: 
            if node==0: path.append(-1)
            else: path.append(cluster[node-1]-1)
        index_of_hub = path.index(-1)
        path = path[index_of_hub:]+path[:index_of_hub]
        all_routes.append(path[:])
    
    for i in range(len(distribution)):
        for j in range(len(distribution[i])):
            distribution[i][j]-=1
    
    global_data_info = []
    documents = []
    for index, route in enumerate(all_routes):
        data = {
            "rider_id": distribution_info.rider_phone_nos[index],
            "item_info": []
        }
        for node in route:
            item_id = ""
            if node!=-1: item_id = item_id = distribution_info.item_ids[node]
            else: item_id = "Hub"
            data['item_info'].append(db.item.find_one({"id": item_id}, {"_id": 0}))
            db.item.update_one({"id": item_id}, {"$set": {"control.is_assigned": True,
                                                          "control.is_fulfilled": False,
                                                          "control.is_cancelled": False}})
        
        data['item_info'].append(db.item.find_one({"id": "Hub"}, {"_id": 0}))
        document = {
            "rider_id": distribution_info.rider_phone_nos[index],
            "rider_location": [hub_lat_long],
            "bag_description": {
                "length": 400000**(1/3),
                "breadth": 400000**(1/3),
                "height": 400000**(1/3)
            },
            "items_in_order": data['item_info'],
            "route_otp": random.randint(10000, 99999),
        }
        global_data_info.append(data)
        documents.append(document)
        
    db.route.insert_many(documents)
    # return global_data_info
    return {"distribution": distribution, "routes": all_routes, "time_taken": time()-start, "total_cost": total_cost}

@router.delete("/delete-pickup/{item_id}")
async def delete_pickup(item_id: str):
    item_info = db.item.find_one({"id": item_id, 
                                  "control.is_assigned": True, 
                                  "control.is_pickup": True}, {"_id": 0})
    if not item_info: 
        raise HTTPException(status_code=404, detail=f"Item does not exist or is not a pickup: {item_id}")
    route_info = db.route.update_one({"id": item_id}, {"$pull": {"items_in_order": {"id": item_id}}})
    db.item.update_one({"id": item_id}, {"$set": {"control.is_assigned": False,
                                                    "control.is_pickup": False,
                                                    "control.is_fulfilled": True,
                                                    "conrtol.is_cancelled": False,
                                                    "control.is_delivery": True}})
    return db.item.find_one({"id": item_id}, {"_id": 0})

@router.put("/add-pickup/{item_id}")
async def add_pickup(item_id: str):
    item_info = db.item.find_one({"id": item_id, 
                                  "control.is_fulfilled": True,
                                  "control.is_assigned": False, 
                                  "control.is_cancelled": False}, {"_id": 0})
    if not item_info:
        raise HTTPException(status_code=404, detail=f"Item is cancelled, assigned or fulfilled: {item_id}")
    
    item_lat_long = tuple(item_info["location"].values())
    all_routes = list(db.route.find({}))
    min_cost_index_volume_bags = []
    for route in all_routes:
        item_dims = tuple(item_info["description"].values())
        bag_dims = tuple(route["bag_description"].values())
        cost_index_volume_bag = {
            "bag": bag_dims[0]*bag_dims[1]*bag_dims[2],
            "volume": item_dims[0]*item_dims[1]*item_dims[2],
            "cost": float('inf'),
            "index": None
        }
        for i in range(len(route["items_in_order"])):
            item_dims = tuple(route["items_in_order"][i]["description"].values())
            cost_index_volume_bag["volume"] += item_dims[0]*item_dims[1]*item_dims[2]
            if cost_index_volume_bag["volume"] > cost_index_volume_bag["bag"]: break
            
            a = tuple(route['rider_location'][-1].values()) if i==0 else tuple(route["items_in_order"][i-1]["location"].values())
            b = tuple(route["items_in_order"][i]["location"].values())
            if road_distance(a, item_lat_long) + road_distance(item_lat_long, b) - road_distance(a, b)<cost_index_volume_bag["cost"]:
                cost_index_volume_bag["cost"] = road_distance(a, item_lat_long) + road_distance(item_lat_long, b) - road_distance(a, b)
                cost_index_volume_bag["index"] = i
        
        min_cost_index_volume_bags.append(list(cost_index_volume_bag.values()))
    
    min_cost_index_volume_bags.sort(key=lambda x: x[2])
    db.item.update_one({"id": item_id}, {"$set": {"control.is_pickup": True,
                                                    "control.is_fulfilled": False,
                                                    "conrtol.is_cancelled": False,
                                                    "control.is_delivery": False}})
    for min_cost_index_volume_bag in min_cost_index_volume_bags:
        if min_cost_index_volume_bag[3]:
            if min_cost_index_volume_bag["volume"]<min_cost_index_volume_bag["bag"]:
                db.route.update_one({"rider_id": route["rider_id"]}, 
                                    {"$push": {"items_in_order": item_info,
                                               "$position": min_cost_index_volume_bag["index"]}})
                db.item.update_one({"id": item_id}, {"$set": {"control.is_assigned": True}})
                return {"item_info": item_info, "is_assigned": True, "index": min_cost_index_volume_bag["index"]}
    
    db.item.update_one({"id": item_id}, {"$set": {"control.is_assigned": False}})
    return {"item_info": db.item.find_one({"id": item_id}, {"_id": 0}), 
            "is_assigned": False, 
            "index": None}


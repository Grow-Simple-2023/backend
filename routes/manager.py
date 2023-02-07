import json
import random
import tempfile
import subprocess
import pandas as pd
import multiprocessing
from services.auth import *
from time import time, sleep
from datetime import datetime
from config.db_config import db
from pymongo import ReturnDocument
from services.multiprocess import *
from models.model import DistributeModel
from services.Clustering import Clustering
from services.TSP import TSP, road_distance
from fastapi import APIRouter, HTTPException, Request, Depends, File, UploadFile
from services.get_geojson import get_geojson

router = APIRouter()


def is_in_bang(point, coordinates=[12.853789, 77.425682, 13.101558, 77.744427]):
    x, y = point
    x_min, y_min, x_max, y_max = coordinates
    if x_min <= x <= x_max and y_min <= y <= y_max:
        return True
    else:
        return False


@router.get("/")
async def manager_home(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    return {"message": "Welcome to Grow-Simplee Manager API"}


@router.get("/users")
async def get_users(load: str = Depends(decode_jwt)):
    check_role(load, ["ADMIN"])
    users = []
    for user in db.user.find():
        del user["_id"]
        users.append(user)
    return users


# to calculate on time delivery percentage
@router.get("/OTD-percentage")
async def on_time_delivery_percentage(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    no_of_successful_deleveries = db.item.count_documents({"EDD": {"$lte": str(datetime.now())},
                                                           "control.is_fulfilled": True,
                                                           "$expr": {"$lte": ["$delivered_on", "$EDD"]},
                                                           "control.is_cancelled": False})

    total_deliveries_to_be_done = db.item.count_documents({"EDD": {"$lte": str(datetime.now())},
                                                           "control.is_cancelled": False})

    percentage_of_successful_deliveries = (
        no_of_successful_deleveries/total_deliveries_to_be_done)*100
    return {"percentage": percentage_of_successful_deliveries}

# items in delivery


@router.get("/items-in-delivery")
async def current_items_in_delivery(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    items_in_delivery = list(db.route.find(
        {}, {"_id": 0}))
    return {"items_in_delivery": items_in_delivery}


@router.get("/items/{item_id}")
async def get_item(item_id: str, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    item = db.item.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(
            status_code=404, detail=f"Item not found: {item_id}")
    return {"item": item}


@router.get("/unassigned-items")
async def unassigned_items(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    documents = list(db.item.find({"control.is_fulfilled": False,
                                   "control.is_assigned": False,
                                   "control.is_cancelled": False}, {"_id": 0}))
    return {"unassigned_items": documents}


@router.get("/riders")
async def get_rider(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    documents = list(db.user.find({"role": "RIDER"}, {"_id": 0}))
    return {"riders": documents}


@router.get("/unassigned-riders")
async def get_unassigned_rider(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    a_riders = []
    assigned_riders = list(db.route.find({}, {"_id": 0}))
    for rider in assigned_riders:
        a_riders.append(rider["rider_id"])
    documents = list(db.user.find(
        {"phone_no": {"$nin": assigned_riders}, "role": "RIDER"}, {"_id": 0}))
    return {"unassigned_riders": documents}


@router.get("/riders/{rider_no}")
async def get_rider(rider_no: str, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    rider = db.user.find_one(
        {"phone_no": rider_no, "role": "RIDER"}, {"_id": 0})
    if not rider:
        raise HTTPException(
            status_code=404, detail=f"Rider not found: {rider_no}")
    return {"rider": rider}


@router.get("/delivered")
async def get_delivered_items(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    return {"delivered_items": list(db.item.find({"control.is_delivery": True, "control.is_fulfilled": True}, {"_id": 0}))}


@router.get("/in-pickup")
async def get_items_in_pickup(user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    return {"items_in_pickup": list(db.item.find({"control.is_pickup": True, "control.is_fulfilled": False}, {"_id": 0}))}


@router.post("/distribute")
async def distribute_items(distribution_info: DistributeModel, user_data=Depends(decode_jwt)):
    rider_volume = 15**3 * 20
    check_role(user_data, ["ADMIN"])
    start = time()
    hub_lat_long = db.item.find_one({"id": "Hub"})["location"]
    hub_location = tuple(hub_lat_long.values())
    no_riders = len(distribution_info.rider_phone_nos)

    matching_riders_count = db.user.count_documents(
        {"phone_no": {"$in": distribution_info.rider_phone_nos}, "role": "RIDER"})

    if matching_riders_count != no_riders:
        raise HTTPException(
            status_code=404, detail=f"One of the Phone numbers does not belong to a rider")

    item_info = list(db.item.aggregate([
        {"$match": {
            "id": {"$in": distribution_info.item_ids},
            "control.is_assigned": False,
            "control.is_fulfilled": False,
            "control.is_cancelled": False
        }},
        {"$project": {
            "description": {
                "height": "$description.height",
                "breadth": "$description.breadth",
                "length": "$description.length"
            },
            "location": {
                "latitude": "$location.latitude",
                "longitude": "$location.longitude"
            },
            "EDD": "$EDD"
        }}
    ]))

    item_dims, item_lat_long, EDD = [], [], []

    if len(item_info) != len(distribution_info.item_ids):
        missing_item_ids = set(distribution_info.item_ids) - \
            set(item["id"] for item in item_info)
        raise HTTPException(
            status_code=404, detail=f"Item does not exist or is already assigned: {missing_item_ids}")
    else:
        item_dims = [tuple(item["description"].values()) for item in item_info]
        item_lat_long = [tuple(item["location"].values())
                         for item in item_info]
        EDD = [item["EDD"] for item in item_info]

    rider_vol = [rider_volume for _ in range(no_riders)]
    cluster = Clustering(item_dims, item_lat_long, no_riders, rider_vol, EDD)
    distribution = cluster.distribute()

    distribution = [[elem + 1 for elem in row] for row in distribution]

    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    return_list = manager.list()
    return_dict["total_cost"] = 0
    return_dict["all_routes"] = []
    processes = []

    for cluster in distribution:
        process = multiprocessing.Process(target=tsp_calculation,
                                          args=(cluster, hub_location, item_lat_long, return_dict, return_list))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    all_routes = list(return_list)
    total_cost = return_dict["total_cost"]

    distribution = [[elem - 1 for elem in row] for row in distribution]
    print(len(all_routes))
    documents = []
    for index, route in enumerate(all_routes):
        rider_id = distribution_info.rider_phone_nos[index]
        item_ids = [distribution_info.item_ids[node]
                    if node != -1 else "Hub" for node in route]
        item_docs = list(db.item.find(
            {"id": {"$in": item_ids + ["Hub"]}}, {"_id": 0}))
        item_info_dict = {doc["id"]: doc for doc in item_docs}
        item_info = [item_info_dict[item_id] for item_id in item_ids]
        document = {
            "rider_id": rider_id,
            "route_start": str(datetime.now()),
            "rider_location": [hub_lat_long],
            "bag_description": {
                "length": rider_volume**(1/3),
                "breadth": rider_volume**(1/3),
                "height": rider_volume**(1/3)
            },
            "items_in_order": item_info + [doc for doc in item_docs if doc["id"] == "Hub"],
            "route_otp": random.randint(10000, 99999),
            "last_modified": str(datetime.now()),
        }
        documents.append(document)

    db.route.insert_many(documents)
    db.item.update_many({"id": {"$in": item_ids}}, {"$set": {
                        "control.is_assigned": True, "control.is_fulfilled": False, "control.is_cancelled": False}})

    return {"routes": list(db.route.find({}, {"_id": 0})), "time_taken": time()-start, "total_cost": total_cost}


@router.delete("/delete-pickup/{item_id}")
async def delete_pickup(item_id: str, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])

    item_doc = db.item.find_one_and_update(
        {"id": item_id,
         "control.is_pickup": True},
        {"$set": {
            "control.is_assigned": False,
            "control.is_pickup": False,
            "control.is_fulfilled": True,
            "control.is_cancelled": False,
            "control.is_delivery": True
        }},
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0}
    )
    if not item_doc:
        raise HTTPException(
            status_code=404, detail=f"Item does not exist or is not a pickup: {item_id}")

    route_doc = db.route.find_one_and_update(
        {"items_in_order.id": item_id},
        {"$pull": {"items_in_order": {"id": item_id}}},
        return_document=ReturnDocument.AFTER,
        projection={"_id": 0}
    )
    if route_doc:
        db.route.update_one(
            {"rider_id": route_doc["rider_id"]},
            {"$set": {"last_modified": str(datetime.now())}}
        )

    return {"removed_pickup": item_doc}


@router.put("/add-pickup/{item_id}")
async def add_pickup(item_id: str, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])

    item_query = {
        "id": item_id,
        "control.is_fulfilled": True,
        "control.is_delivery": True,
        "control.is_pickup": False,
        "control.is_assigned": False,
        "control.is_cancelled": False
    }

    item_info = db.item.find_one(item_query, {"_id": 0})
    if not item_info:
        raise HTTPException(
            status_code=404, detail=f"Item is cancelled, assigned or fulfilled: {item_id}")

    item_lat_long = tuple(item_info["location"].values())
    item_dims = tuple(item_info["description"].values())

    route_query = {}

    all_routes = list(db.route.find(route_query))
    min_cost_index_volume_bags = []

    for route in all_routes:
        bag_dims = tuple(route["bag_description"].values())
        cost_index_volume_bag = {
            "bag": bag_dims[0] * bag_dims[1] * bag_dims[2],
            "volume": item_dims[0] * item_dims[1] * item_dims[2],
            "cost": float('inf'),
            "index": None,
            "rider_id": route["rider_id"]
        }

        for i in range(len(route["items_in_order"])):
            if route["items_in_order"][i]["id"] != "Hub":
                temp_item_dims = tuple(
                    route["items_in_order"][i]["description"].values())
            else:
                temp_item_dims = (0, 0, 0, 0)

            cost_index_volume_bag["volume"] += temp_item_dims[0] * \
                temp_item_dims[1] * temp_item_dims[2]
            if cost_index_volume_bag["volume"] > cost_index_volume_bag["bag"]:
                break

            a = tuple(route['rider_location'][-1].values()) if i == 0 else tuple(
                route["items_in_order"][i-1]["location"].values())
            b = tuple(route["items_in_order"][i]["location"].values())

            if road_distance(a, item_lat_long) + road_distance(item_lat_long, b) - road_distance(a, b) < cost_index_volume_bag["cost"]:
                cost_index_volume_bag["cost"] = road_distance(
                    a, item_lat_long) + road_distance(item_lat_long, b) - road_distance(a, b)
                cost_index_volume


@router.post("/load_items")
async def load_excel(file: UploadFile, user_data=Depends(decode_jwt)):
    check_role(user_data, ["ADMIN"])
    file_content = await file.read()

    if not os.path.exists("./services/temp_files"):
        os.makedirs("./services/temp_files")
    x_file_name = "./services/temp_files/"+f"{random.randint(1, 9999999)}.xlsx"

    with open(x_file_name, "wb") as f:
        f.write(file_content)

    df = pd.read_excel(x_file_name)

    try:
        df = df.drop(columns=["Unnamed: 0"])
    except:
        pass

    os.remove(x_file_name)

    N = len(df)

    random_file = f"{random.randint(10000, 99999)}.json"
    with open("./services/temp_files/"+random_file, "w+") as f:
        json.dump({"adds": df["address"].tolist()}, f)

    out = subprocess.run(
        ["python", "./services/geocode_file.py", random_file])

    with open("./services/temp_files/"+random_file, "r") as f:
        lat_longs = json.load(f)

    lat_longs = lat_longs["ll"]

    os.remove("./services/temp_files/"+random_file)

    # lat_longs = [(random.uniform(12, 13), random.uniform(77, 78))
    #              for i in range(N)]

    def sum_of_chars(s: str) -> int:
        return sum(ord(c) for c in s)

    try:
        for lat_long in lat_longs:
            assert lat_long[0] != None and lat_long[1] != None
        assert len(lat_longs) == N
    except:
        raise HTTPException(
            status_code=400, detail="Addresses could not be resolved to a location")

    documents, docs = [], []

    try:
        phone_nos = df["phone_no"].tolist()
    except:
        phone_nos = df["AWB"].tolist()

    for i in range(N):
        now = str(datetime.now())
        otp_hash = sum_of_chars(now+str(lat_longs[i][0])+str(lat_longs[i][1]))
        is_cancelled = not is_in_bang(
            (float(lat_longs[i][0]), float(lat_longs[i][1])))
        document = {
            "id": str(phone_nos[i]),
            "product_id": df["product_id"][i],
            "title": f"Watch {i}",
            "description": {
                "length": float(random.uniform(10, 20)),
                "breadth": float(random.uniform(10, 20)),
                "height": float(random.uniform(10, 20)),
                "weight": float(random.uniform(10, 20))
            },
            "address": df["address"][i],
            "location": {
                "latitude": float(lat_longs[i][0]),
                "longitude": float(lat_longs[i][1])
            },
            # TODO: Add EDD from file
            "EDD": now,
            "control": {
                "is_assigned": False,
                "is_fulfilled": False,
                "is_pickup": False,
                "is_delivery": True,
                "is_cancelled": is_cancelled
            },
            "OTP": int(str((otp_hash % 9) + 1) + str(otp_hash % 10000)),
            "delivered_on": None,
            "phone_no": str(phone_nos[i])
        }
        documents.append(document)
    db.item.insert_many(documents)
    for i in range(N):
        del documents[i]["_id"]
    return {"data": "Data loaded successfully"}

@router.get("/submission-files")
async def get_submission_files():
    documents = list(db.route.find({}))
    riders_route = {}
    for document in documents:
        route = []
        for item in document["items_in_order"]:
            route.append([item["location"]["latitude"],item["location"]["longitude"]])
        riders_route[document["rider_id"]] = route
    riders_route_distance = {}
    for rider_id in riders_route:
        res = get_geojson(riders_route[rider_id], "./geojson/"+rider_id+".json")
        riders_route_distance[rider_id] = res
    return {"data": riders_route_distance}

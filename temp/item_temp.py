import json
import random
from datetime import datetime, timedelta
items = []

for i in range(1000):
    item = {}
    item["id"] = "object"+str(i)
    item["title"] = "title"+str(i)
    l = random.uniform(10,20)
    b = random.uniform(10,20)
    h = random.uniform(10,20)
    w = random.uniform(10,30)
    dec = {}
    dec["length"] = l
    dec["breadth"] = b
    dec["height"] = h
    dec["weight"] = w
    item["description"] = dec
    item["address"] = "address"+str(i)
    location = {
        "latitude": random.uniform(1,30),
        "longitude": random.uniform(50,100)
    }
    item["location"] = location
    edd = datetime.now()+timedelta(days=random.randint(-3,3))
    item["EDD"] = str(edd)
    ful = random.choice([True,False])
    is_del = random.choice([True,False])
    control = {
        "is_fulfilled": ful,
		"is_delivery": is_del,
		"is_pickup": random.choice([False, not is_del]),
		"is_assigned":False,
		"is_cancelled": False
    }
    item["control"] = control
    item["OTP"] = random.randint(10000,99999)
    list_on = [None, str(edd + timedelta(days=random.randint(0, 2)))]
    item["delivered_on"] = list_on[ful]
    items.append(item)


file = open("./item.json","w")
json.dump(items,file,indent=4)

print("completed")

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
    control = {
        "is_fulfilled": random.choice([True,False]),
		"is_delivery": random.choice([True,False]),
		"is_pickup": random.choice([True,False]),
		"is_assigned":random.choice([True,False]), 
		"is_cancelled": random.choice([True,False]),
    }
    item["control"] = control
    item["OTP"] = random.randint(10000,99999)
    item["delivered_on"] = random.choice([None, str(edd + timedelta(days=random.randint(0, 2)))])
    items.append(item)


file = open("./item.json","w")
json.dump(items,file,indent=4)

print("completed")

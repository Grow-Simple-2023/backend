import requests
import time
import json
import sys


with open('total.json') as f:
    total = json.load(f)['data']

with open('items_1_1.json') as f:
    items = json.load(f)['delivered_items']

def item_status_update(item_id, status, rider_id):
    url = f'http://10.196.7.155:8000/rider/item-status-update/{rider_id}/'
    data = {'item_id': item_id, 'status': status,'OTP':0}
    r = requests.post(url, json=data)
    return r

def update_rider_location(rider_id,lat_long):
    url = f'http://10.196.7.155:8000/rider/send-self-location/{rider_id}/'
    data = {'latitude': lat_long[0], 'longitude': lat_long[1], 'timestamp': time.time()}
    r = requests.post(url, json=data)
    print(r)
    return r

def get_all_routes():
    url = 'http://10.196.7.155:8000/manager/items-in-delivery/'
    r = requests.get(url)
    res = r.json()
    print(res)
    return res['items_in_delivery']

all_routes = get_all_routes()

# print(all_routes)
# for route in all_routes:
#     rider_id = route['rider_id']
#     items = route['items_in_order']
#     total_items = len(items)
#     actual_time = float(sys.argv[1])/60
#     total_time = total[rider_id][1]
#     last_item_index = int(min(total_items, total_items * (actual_time/total_time)))
#     for i in range(last_item_index):
#         item_id = items[i]['id']
#         item_status_update(item_id, 1, rider_id)
#         update_rider_location(rider_id, (items[i]['location']['latitude'], items[i]['location']['longitude']))

def add_pickup(item_id):
    url = f'http://10.196.7.155:8000/manager/add-pickup/{item_id}/'
    r = requests.put(url)
    print(r)
    return r

for item in items:
    add_pickup(item['id'])


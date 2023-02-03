import sys
import json
import aiohttp
import asyncio
import requests
import requests
import urllib.parse
from typing import List


API_KEY = "3c4eacd7b94417c93f4bc00150e310e1"


def distance_matrix(coordinates):
    coordinates_string = ""
    for coordinate in coordinates:
        coordinates_string += f"{coordinate[0]},{coordinate[1]};"
    url = f"https://api.mapbox.com/directions-matrix/v1/mapbox/driving-traffic/{coordinates_string}"
    response = requests.get(url)
    response_json = response.json()
    return response_json


async def send_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def geocode_helper(addresses: List[str]) -> List[List[float]]:
    urls = [
        f"https://geokeo.com/geocode/v1/search.php?q={urllib.parse.quote(address)}&api={API_KEY}" for address in addresses]
    tasks = [asyncio.ensure_future(send_request(url)) for url in urls]
    responses = await asyncio.gather(*tasks)

    lat_longs = []
    for url, response in zip(urls, responses):
        try:
            response_json = json.loads(response)
            lat = response_json['results'][0]['geometry']['location']['lat']
            long = response_json['results'][0]['geometry']['location']['lng']
            lat_longs.append([lat, long])
        except:
            lat_longs.append((None, None))

    return lat_longs


with open("./services/temp_files/"+sys.argv[1], "r") as f:
    addresses = json.load(f)

print("Hello")

addresses = addresses["adds"]
loop = asyncio.get_event_loop()
lat_longs = loop.run_until_complete(geocode_helper(addresses))

with open("./services/temp_files/"+sys.argv[1], "w+") as f:
    json.dump({"ll": lat_longs}, f)

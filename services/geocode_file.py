import sys
import json
import aiohttp
import asyncio
import requests
import requests
import urllib.parse
from time import sleep
from typing import List
from tqdm import tqdm


API_KEY = ["3c4eacd7b94417c93f4bc00150e310e1", "d303a35b42b86c32f5e2631898684aa3",
           "3324a57d1d08421bedd7958ce4c13d97", "0b6ef7a460acb75d81ef6c85f8b474f4", "c31e0456f0f0d56b200621e548344e9a"]


async def send_request(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


def geocode_helper(addresses: List[str]) -> List[List[float]]:
    urls = [
        f"https://geokeo.com/geocode/v1/search.php?q={urllib.parse.quote(address)}&api={API_KEY[index%len(API_KEY)]}" for index, address in enumerate(addresses)]
    # tasks = [asyncio.ensure_future(send_request(url)) for url in urls]
    # responses = await asyncio.gather(*tasks)
    responses = []
    for url in tqdm(urls):
        response = requests.get(url)
        responses.append(response.text)
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

print("started")
final_lat_longs = []
index, step = 0, 10
while index < len(addresses["adds"]):
    print(index)
    addresses_temp = addresses["adds"][index:min(
        index+step, len(addresses["adds"]))]
    # loop = asyncio.get_event_loop()
    # lat_longs = loop.run_until_complete(geocode_helper(addresses_temp))
    lat_longs = geocode_helper(addresses_temp)
    index += step
    final_lat_longs += lat_longs
    sleep(2)

with open("./services/temp_files/"+sys.argv[1], "w+") as f:
    json.dump({"ll": final_lat_longs}, f)

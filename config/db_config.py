import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("MONGO_ROOT_USERNAME")
password = os.getenv("MONGO_ROOT_PASSWORD")
connection_url = f"mongodb://{username}:{password}@10.196.7.155:27018"
client = MongoClient(connection_url)
db = client.get_database("grow-simplee")

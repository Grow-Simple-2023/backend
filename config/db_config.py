import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("MONGO_ROOT_USERNAME")
password = os.getenv("MONGO_ROOT_PASSWORD")
connection_url = f"mongodb://{username}:{password}@10.250.61.56:27018"
client = MongoClient(connection_url)
db = client.get_database("grow-simplee")

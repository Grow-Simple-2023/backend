import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("MONGO_INITDB_ROOT_USERNAME")
password = os.getenv("MONGO_INITDB_ROOT_PASSWORD")
connection_url = f"mongodb://{username}:{password}@mongodb:27017"
client = MongoClient(connection_url)
db = client.get_database("grow_simplee")

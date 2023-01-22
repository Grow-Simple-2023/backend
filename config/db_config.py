import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")
connection_url = f"mongodb+srv://{username}:{password}@cluster0.iy0bw.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_url)
db = client.get_database("grow_simplee")

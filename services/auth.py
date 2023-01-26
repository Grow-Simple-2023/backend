import os
import jwt
from time import time
import json
from models.model import *
from dotenv import load_dotenv
from config.db_config import db
from fastapi import HTTPException, status, Request



def check_user_exists(phone_no):
    print(db.user.find_one({"phone_no":  phone_no}))
    print("hello world")
    user = None
    try:
        user = db.user.find_one({"phone_no":phone_no})
    except Exception as e:
        print(e) 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Database Error")
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    return 

def add_new_user(phone_no, first_name, last_name, password, role ):
    print("hello world from add new user function ")
    try:
        result = db.user.insert_one({
            "name":{
            "first": first_name,
            "last": last_name
            },
            "phone_no": phone_no,
            "password":password,
            "role":[role]
        })
        try:
            user = db.user.find_one({"phone_no": phone_no})
            del user["_id"]
            if user:
                return {
                    "user": user,
                    "message": "User added successfully!"
                }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
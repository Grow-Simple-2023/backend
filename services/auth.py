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
            "role":role
        })
        try:
            user = db.user.find_one({"phone_no": phone_no})
            del user["_id"]
            if user:
                return user
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
  

def verify_credentials(phone_no, password):
  try:
      user = db.user.find_one({"phone_no": phone_no, "password": password})
      print(user)
      del user['_id']
      if user:
          return {
              "phone_no": user["phone_no"],
              "role": user["role"]
          }
      else:
          raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found. Please enter correct credentials!")
  except Exception as e:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Please enter correct credentials")


def create_token(phone_no, role):
    exp = 3600 * float(os.getenv("TOKEN_EXP")) * 24
    encoded = jwt.encode({"phone_no": phone_no, "role": role, "exp": int(time())+exp}, os.getenv("PRIVATE_KEY"), algorithm="HS256")
    token = Token(**{"access_token": encoded, "token_type": "Bearer"})
    return token
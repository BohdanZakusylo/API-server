import jwt
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from datetime import datetime
from fastapi import HTTPException
import random
import string
import app.common as common
import app.connection as connection


conn, cursor = connection.conn, connection.cursor

load_dotenv(".env")

PATH_PRIVATE_KEY = os.getenv("PRIVATE_KEY")
PATH_PUBLIC_KEY = os.getenv("PUBLIC_KEY")

with open(PATH_PRIVATE_KEY, "r") as file:
    private_key = file.read()

with open(PATH_PUBLIC_KEY, "r") as file:
    public_key = file.read()


def encode_token(id: int, name: str) -> str:
    dict_to_encode = {
        "id": id,
        "username": name,
        "expiration_time": datetime.utcnow().timestamp() + 3600 
    }

    encoded_token = jwt.encode(dict_to_encode, private_key, algorithm="RS256")

    return encoded_token

def decode_token(token: str):
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])

        if decoded_token["expiration_time"] < datetime.utcnow().timestamp():
             raise HTTPException(status_code=401, detail="token is expired")
        
        if "type" in decoded_token:
            raise HTTPException(status_code=403, detail="resfresh token is not allowed")

    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="token is invalid")
    
    except KeyError:
        raise HTTPException(status_code=401, detail="token is invalid")

    return decoded_token

def encode_refresh_token() -> str:
    
    length = 10
    random_string = ''.join(random.choice(string.ascii_letters) for _ in range(length))
    
    dict_to_encode = {
        "random_string": random_string,
        "expiration_time": datetime.utcnow().timestamp() + 3600 * 24 * 365
    }

    encoded_token = jwt.encode(dict_to_encode, private_key, algorithm="RS256")

    return encoded_token

def decode_refresh_token(token: str):
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])

        if decoded_token["expiration_time"] < datetime.utcnow().timestamp():
             raise HTTPException(status_code=401, detail="token is expired")

    except jwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="token is invalid")
    
    except KeyError:
        raise HTTPException(status_code=401, detail="token is invalid")
    
    try:
        cursor.execute(f"SELECT [user].user_id, [user].username FROM [user] WHERE [user].refresh_token = '{token}';")

        results = cursor.fetchall()

        for row in results:
            user_id, name = row
        
    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=401, detail="Refresh token is incorrect")
    
    except TypeError:
        raise common.HTTPException(status_code=401, detail="Refresh token does not exist")

    return [user_id, name]
    




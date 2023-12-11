import jwt
import os
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

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
        "name": name,
    }

    encoded_token = jwt.encode(dict_to_encode, private_key, algorithm="RS256")

    return encoded_token

def decode_token(token: str):
    try:
        decoded_token = jwt.decode(token, public_key, algorithms=["RS256"])
    except jwt.exceptions.DecodeError:
        return "token is invalid"
    
    return decoded_token




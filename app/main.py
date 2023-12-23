import os
import pyodbc
import hashlib
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from app.token_generator.token_validation import encode_token, decode_token, encode_refresh_token
from app.data_type_validation.data_validate import Correct_Data
from datetime import datetime
from app.base_classes.login_info import LoginInfo


ACCEPTED_DATA_TYPES = ["xml", "json"];
correct_data = Correct_Data()


app = FastAPI()

load_dotenv(".env")

SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")


connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes'

conn = pyodbc.connect(connectionString)
cursor = conn.cursor()



@app.get("/")
async def main_page():
    return {"message": "Hello World"}


@app.post("/registration")
async def login(login_info: LoginInfo):
    try:
        query = """EXECUTE [InsertUser] @email = ?, @password = ?, @nick_name = ?, @age = ?;"""
        password_bytes = login_info.password.encode('utf-8')
        hashed_password = hashlib.sha256(password_bytes).hexdigest()
        cursor.execute(query, login_info.email, hashed_password, login_info.nick_name, login_info.age)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Email should be unique")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].email = '{login_info.email}';")


    return {
        "token": encode_token(cursor.fetchone()[0], login_info.nick_name),
        "refresh_token": encode_refresh_token(cursor.fetchone()[0], login_info.nick_name)
    }


@app.get("/new-token")
def get_token_by_refresh_token(refresh_token: str = Query(...)):
    decoded_token = decode_token(refresh_token)

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].user_id = {decoded_token['id']};")

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "token": encode_token(decoded_token["id"], decoded_token["name"]),
    }


@app.get("/select/{entity}/{id}/{data_type}")
async def get_data_by_id(entity: str, id: int, data_type: str, token : str = Query(...)):
    entity = entity.lower()

    #Start of the code that checks if the token is valid and if the data type is valid

    correct_data.validate_data_type(data_type)

    decode_token(token)

    #End of the code that checks if the token is valid and if the data type is valid

    cursor.execute(f"SELECT * FROM [{entity}] WHERE [{entity}].{entity}_id = {id};")
    rows = cursor.fetchall()

    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = row[idx]
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, entity)


@app.get("/select/{entity}/{data_type}")
async def get_data_by_id(entity: str, data_type: str, token : str = Query(...)):
    entity = entity.lower()
    #Start of the code that checks if the token is valid and if the data type is valid
    correct_data.validate_data_type(data_type)

    if decode_token(token) == "token is invalid":
        raise HTTPException(status_code=401, detail="token is invalid")
    #End of the code that checks if the token is valid and if the data type is valid

    cursor.execute(f"SELECT * FROM [{entity}];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = row[idx]
        result_list.append(user_dict)
    
    return correct_data.return_correct_format(result_list, data_type, entity)

@app.get("/view/{view_name}/{data_type}")
async def get_data_by_id(view_name: str, data_type: str, token : str = Query(...)):
    view_name = view_name.lower()
    #Start of the code that checks if the token is valid and if the data type is valid
    correct_data.validate_data_type(data_type)

    if decode_token(token) == "token is invalid":
        raise HTTPException(status_code=401, detail="token is invalid")
    #End of the code that checks if the token is valid and if the data type is valid

    cursor.execute(f"SELECT * FROM [dbo].[{view_name}];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = row[idx]
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, view_name)

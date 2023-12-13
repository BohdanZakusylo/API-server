import os
import pyodbc
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from app.token_generator.token_validation import encode_token, decode_token
from app.data_type_validation.data_validate import Correct_Data
from datetime import datetime
from typing import Optional


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
async def login(email: str = Query(...), password: str = Query(...), nick_name: str = Query(...), age: int = Query(...)):
    #TODO hash password
    try:
        query = """EXECUTE [InsertUser] @email = ?, @password = ?, @nick_name = ?, @age = ?;"""
        cursor.execute(query, email, password, nick_name, age)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Email should be unique")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].email = '{email}';")

    return encode_token(cursor.fetchone()[0], nick_name)


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

import os
import pyodbc
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from app.token_generator.token_validation import encode_token, decode_token
from app.data_type_validation.data_validate import return_correct_data
from datetime import datetime

# main connection variables

app = FastAPI()

# load_dotenv(".env")

# SERVER = os.getenv("SERVER")
# DATABASE = os.getenv("DATABASE")
# USERNAME = os.getenv("USER")
# PASSWORD = os.getenv("PASSWORD")


# connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes'

# conn = pyodbc.connect(connectionString)


@app.get("/")
async def main_page():
    return {"message": "Hello World"}


@app.post("/login")
async def login(name: str = Query(...), password: str = Query(...), email: str = Query(...)):
    return {f"token: {encode_token(1, name)}"}

@app.get("/get")
async def get_props(token: str):
    return decode_token(token)


import os
import pyodbc
from dotenv import load_dotenv
from fastapi import FastAPI

# main connection variables

app = FastAPI()

load_dotenv("./.env")

SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes'

conn = pyodbc.connect(connectionString)


@app.get("/")
async def root():
    return {"message": "Hello World"}

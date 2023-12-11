import os
import pyodbc
from dotenv import load_dotenv
from fastapi import FastAPI, Query

# main connection variables

app = FastAPI()

# load_dotenv(".env")

# SERVER = os.getenv("SERVER")
# DATABASE = os.getenv("DATABASE")
# USERNAME = os.getenv("USER")
# PASSWORD = os.getenv("PASSWORD")
PUBLIC_KEY = os.getenv("PUBLiC_KEY")


# connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes'

# conn = pyodbc.connect(connectionString)


@app.get("/")
async def main_page():
    return {"message": "Hello World"}


@app.post("/login")
async def login(name: str = Query(...), password: str = Query(...), email: str = Query(...)):


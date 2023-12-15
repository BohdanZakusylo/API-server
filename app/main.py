import os
import pyodbc
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from app.token_generator.token_validation import encode_token, decode_token
from app.data_type_validation.data_validate import Correct_Data
from datetime import datetime
from typing import Optional


ACCEPTED_DATA_TYPES = ["xml", "json"]
ACCEPTED_MATERIAL_TYPE = ["Film", "Series", "Episode"]
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

# def foo(**kwargs):
#     print(kwargs)

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

@app.delete("/delete/{entity}/{id}")
async def delete_data_by_id(entity: str, id: str, token: str = Query(...)):
    entity = entity.lower()

    decode_token(token)
    try:
        query = f"DELETE FROM [{entity}] WHERE [{entity}].{entity}_id = {id};"

        cursor.execute(query)
        conn.commit()

        return {"message": f"Record with {entity}_id = {id} deleted successfully."}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

# @app.delete("delete_material/{material_type}/{title}/")
# async def delete_data_by_title(material_type: str, name: str, token: str = Query(...)):
#     # material_type = material_type.lower()
#     # name = name.lower()
#     print(material_type, name, sep='; ', file='/Users/vlladiisslavv/Desktop/text.txt')
#
#     correct_data.validate_material_type(material_type)
#
#     decode_token(token)
#     try:
#         query = f"DELETE FROM [{material_type}] WHERE [title] = '{name}';"
#
#         cursor.execute(query)
#         conn.commit()
#
#         return {"message": f"{material_type} with title = {name} deleted successfully."}
#     except Exception as e:
#         conn.rollback()
#         return {"error": f"Error occurred during deletion: {str(e)}"}

# @app.put("update/")
#Зробити діксіонарі для всіх табличок з доступною інфою і **kwargs який сприймає функція і чекає ліву сторону а потім праву

@app.put("/insert/attribute")
async def insert_attribute(type: str = Query(...), description: str = Query(...)):
    try:
        query = """EXECUTE [InsertAttribute] @attribute_type = ?, @attribute_description = ?;"""
        cursor.execute(query, (type, description))
        conn.commit()

        return {"message": "Successfully inserted attribute"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}


@app.put("/insert/dubbing")
async def insert_dubbing(film_id: int = Query(...), episode_id: int = Query(...), language_id: int = Query(...), dub_company: str = Query(...)):
    try:
        query = """EXECUTE [InsertDubbing] @film_id = ?, @episode_id = ?, @language_id = ?, @dubbing_company = ?;"""
        cursor.execute(query, (film_id, episode_id, language_id, dub_company))
        conn.commit()

        return {"message": "Successfully inserted dubbing"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/episode")
async def insert_episode(series_id: int = Query(...), title: str = Query(...), duration: int = Query(...), episode_number: int = Query(...)):
    try:
        query = """EXECUTE [InsertEpisode] @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"""
        cursor.execute(query, (series_id, title, duration, episode_number))
        conn.commit()

        return {"message": "Successfully inserted episode"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/film")
async def insert_film(title: int = Query(...), duration: int = Query(...)):
    try:
        query = """EXECUTE [InsertFilm,] @title = ?, @duration = ?;"""
        cursor.execute(query, (title, duration))
        conn.commit()

        return {"message": "Successfully inserted film"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/film_genre")
async def insert_film_genre(film_id: int = Query(...), attribute_id: int = Query(...)):
    try:
        query = """EXECUTE [InsertFilmGenre,] @film_id = ?, @attribute_id = ?;"""
        cursor.execute(query, (film_id, attribute_id))
        conn.commit()

        return {"message": "Successfully inserted film_genre"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/film_quality")
async def insert_film_quality(film_id: int = Query(...), quality_id: int = Query(...)):
    try:
        query = """EXECUTE [InsertFilmQuality,] @film_id = ?, @quality_id = ?;"""
        cursor.execute(query, (film_id, quality_id))
        conn.commit()

        return {"message": "Successfully inserted film_quality"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/language")
async def insert_language(language_name: str = Query(...)):
    try:
        query = """EXECUTE [InsertLanguage,] @language_name = ?;"""
        cursor.execute(query, (language_name))
        conn.commit()

        return {"message": "Successfully inserted Language"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/preferred_attribute")
async def insert_preferred_attribute(profile_id: int = Query(...), attribute_id: int = Query(...)):
    try:
        query = """EXECUTE [InsertPreferredAttribute] @profile_id = ?, @attribute_id = ?;"""
        cursor.execute(query, (profile_id, attribute_id))
        conn.commit()

        return {"message": "Successfully inserted preferred attribute"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/profile")
async def insert_profile(user_id: int = Query(...), age: int = Query(...), nick_name: str = Query(...), pfp: str = Query(...)):
    try:
        query = """EXECUTE [InsertProfile] @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"""
        cursor.execute(query, (user_id, age, nick_name, pfp))
        conn.commit()

        return {"message": "Successfully inserted profile"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/quality")
async def insert_quality(type: str = Query(...)):
    try:
        query = """EXECUTE [InsertQuality] @quality_type = ?;"""
        cursor.execute(query, type)
        conn.commit()

        return {"message": "Successfully inserted quality"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/series")
async def insert_series(title: str = Query(...), amount_of_episodes: int = Query(...)):
    try:
        query = """EXECUTE [InsertSeries] @title = ?, @amount_of_episodes = ?;"""
        cursor.execute(query, (title, amount_of_episodes))
        conn.commit()

        return {"message": "Successfully inserted series"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/series_genre")
async def insert_series_genre(series_id: int = Query(...), attribute_id:int = Query(...)):
    try:
        query = """EXECUTE [InsertSeriesGenre] @series_id = ?, @attribute_id = ?;"""
        cursor.execute(query, (series_id, attribute_id))
        conn.commit()

        return {"message": "Successfully inserted series genre"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

@app.put("/insert/subscription")
async def insert_subscription(user_id: int = Query(...), type:str = Query(...), price: float = Query(...), is_discount: bool = Query(...)):
    try:
        query = """EXECUTE [InsertSeriesGenre] @user_id = ?, @type = ?, @price = ?, @is_discount = ?;"""
        cursor.execute(query, (user_id, type, price, is_discount))
        conn.commit()

        return {"message": "Successfully inserted subscription"}
    except Exception as e:
        conn.rollback()
        return {"error": f"Error occurred during deletion: {str(e)}"}

import os
import pyodbc
import hashlib
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, Depends
from app.token_generator.token_validation import encode_token, decode_token, encode_refresh_token, decode_refresh_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.data_type_validation.data_validate import Correct_Data
from bs4 import BeautifulSoup
from datetime import datetime
from app.base_classes.login_info import LoginInfo
from typing import Optional


ACCEPTED_DATA_TYPES = ["xml", "json"]
correct_data = Correct_Data()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app = FastAPI()

load_dotenv(".env")

SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
USERNAME = os.getenv("USER_NAME")
PASSWORD = os.getenv("PASSWORD")


connectionString = f'DRIVER={{ODBC Driver 18 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=yes'

conn = pyodbc.connect(connectionString)
cursor = conn.cursor()

print("Connection established")


@app.get("/")
async def main_page():
    return {"message": "Hello World"}


@app.post("/registration")
async def login(login_info: LoginInfo):
    try:
        query = """EXECUTE [InsertUser] @email = ?, @password = ?, @username = ?, @age = ?;"""
        password_bytes = login_info.password.encode('utf-8')
        hashed_password = hashlib.sha256(password_bytes).hexdigest()
        cursor.execute(query, login_info.email, hashed_password, login_info.username, login_info.age)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Username and email should be unique")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="Username and email should be unique")

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].email = '{login_info.email}';")

    id = cursor.fetchone()[0]

    return {
        "token": encode_token(id, login_info.username)
    }

@app.get("/refresh-token")
def get_refresh_token_by_token(token: str = Depends(oauth2_scheme)):
    decoded_token = decode_token(token)
    
    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].user_id = {decoded_token['id']};")

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "refresh_token": encode_refresh_token(decoded_token["id"], decoded_token["username"]),
    }


@app.get("/new-token")
def get_token_by_refresh_token(refresh_token: str = Depends(oauth2_scheme)):
    decoded_token = decode_refresh_token(refresh_token)

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].user_id = {decoded_token['id']};")

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "token": encode_token(decoded_token["id"], decoded_token["username"]),
    }

#start atributes

@app.get("/atributes/{data_type}")
async def get_atributes(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectAtribute];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "atributes")

@app.get("/atributes/{id}/{data_type}")
async def get_atributes_by_id(id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectAttributeById] @attribute_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "atributes")

@app.post("/atributes")
async def insert_atributes(attribute_type: str = Query(...), attribute_description: str = Query(...), token: str = Depends(oauth2_scheme)):

    decode_token(token)
    
    try:
        query = f"EXEC [InsertAttribute] @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, attribute_type, attribute_description)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Attributes name is incorrect")
    
    return {"message": "Atribute inserted"}

@app.put("/atributes/{id}")
async def update_attributes(id: int, attribute_type: str = Query(...), attribute_description: str = Query(...), token: str = Depends(oauth2_scheme)):

    decode_token(token)

    try: 
        query = f"EXEC [UpdateAttribute] @attribute_id = ?, @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, id, attribute_type, attribute_description)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Attributes naming is incorrect")

    return {"message": "Atribute updated"}

@app.delete("/atributes/{id}")
async def delete_attributes(id: int, token: str = Depends(oauth2_scheme)):

    decode_token(token)

    try:
        query = f"EXEC [DeleteAttribute] @attribute_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Attributes naming is incorrect")

    return {"message": "Atribute deleted"}

#end atributes

#start languages

@app.get("/language/{data_type}")
async def get_languages(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectLanguage];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "languages")


@app.get("/language/{id}/{data_type}")
async def get_languages_by_id(id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectLanguageById] @language_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "languages")

@app.post("/language")
async def insert_languages(language_name: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)
        
    try:
        query = f"EXEC [InsertLanguage] @language_name = ?;"
        cursor.execute(query, language_name)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Language name is incorrect")

    return {"message": "Language inserted"}

@app.put("/language/{id}")
async def update_languages(id: int, language_name: str = Query(...), token: str = Depends(oauth2_scheme)):

    decode_token(token)

    try: 
        query = f"EXEC [UpdateLanguage] @language_id = ?, @language_name = ?;"
        cursor.execute(query, id, language_name)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Language naming is incorrect")

    return {"message": "Language updated"}

@app.delete("/language/{id}")
async def delete_languages(id: int, token: str = Depends(oauth2_scheme)):

    decode_token(token)

    try:
        query = f"EXEC [DeleteLanguage] @language_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Language naming is incorrect")

    return {"message": "Language deleted"}

#end languages

#start profile

@app.get("/profile/{data_type}")
async def get_profile(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectProfile];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "profile")

@app.get("/profile/{id}/{data_type}")
async def get_profile_by_id(id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectProfileById] @profile_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "profile")


@app.post("/profile")
async def insert_profile(user_id: int = Query(...), age: int = Query(...), nick_name: str = Query(...), profile_picture: str = Query(None), token: str = Depends(oauth2_scheme)):
    decode_token(token)
    
    try:
        query = f"EXEC [InsertProfile] @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, user_id, age, nick_name, profile_picture)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Profile data is incorrect")
    
    return {"message": "Profile inserted"}


@app.put("/profile/{id}")
async def update_profile(id: int, user_id: int = Query(...), age: int = Query(...), nick_name: str = Query(...), profile_picture: str = Query(None), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateProfile] @profile_id = ?, @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, id, user_id, age, nick_name, profile_picture)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Profile data is incorrect")

    return {"message": "Profile updated"}

@app.delete("/profile/{id}")
async def delete_profile(id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteProfile] @profile_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Profile data is incorrect")

    return {"message": "Profile deleted"}

#end profile

#start film

@app.get("/film/{data_type}")
async def get_film(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectFilm];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
        
    return correct_data.return_correct_format(result_list, data_type, "film")


@app.get("/film/{id}/{data_type}")
async def get_film_by_id(id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectFilmById] @film_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            if column[0] == "release_date":
                user_dict[column[0]] = str(row[idx])
            else:
                user_dict[column[0]] = row[idx]
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film")

@app.post("/film")
async def insert_film(title: str = Query(...), duration: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertFilm] @title = ?, @duration = ?;"
        cursor.execute(query, title, duration)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film data is incorrect")
    
    return {"message": "Film inserted"}

@app.put("/film/{id}")
async def update_film(id: int, title: str = Query(...), duration: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateFilm] @film_id = ?, @title = ?, @duration = ?;"
        cursor.execute(query, id, title, duration)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film data is incorrect")

    return {"message": "Film updated"}


@app.delete("/film/{id}")
async def delete_film(id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteFilm] @film_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film data is incorrect")

    return {"message": "Film deleted"}

#end film

#start quality

@app.get("/quality/{data_type}")
async def get_quality(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)
    
    decode_token(token)
    
    cursor.execute(f"EXEC [SelectQuality];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
        
    return correct_data.return_correct_format(result_list, data_type, "quality")

@app.get("/quality/{id}/{data_type}")
async def get_quality_by_id(id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)
    
    decode_token(token)

    cursor.execute(f"EXEC [SelectQualityById] @quality_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "quality")

@app.post("/quality")
async def insert_quality(quality_type: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertQuality] @quality_type = ?;"
        cursor.execute(query, quality_type)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Quality data is incorrect")
    
    return {"message": "Quality inserted"}


@app.put("/quality/{id}")
async def update_quality(id: int, quality_type: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateQuality] @quality_id = ?, @quality_type = ?;"
        cursor.execute(query, id, quality_type)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Quality data is incorrect")

    return {"message": "Quality updated"}


@app.delete("/quality/{id}")
async def delete_quality(id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteQuality] @quality_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Quality data is incorrect")

    return {"message": "Quality deleted"}

#end quality

#start subtitle

@app.get("/subtitle/{data_type}")
async def get_subtitle(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectSubtitle];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
        
    return correct_data.return_correct_format(result_list, data_type, "subtitle")

@app.get("/subtitle/{id}/{data_type}")
async def get_subtitle_by_id(id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectSubtitleById] @subtitle_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "subtitle")

@app.post("/subtitle")
async def insert_subtitle(film_id: int = Query(None), episode_id: int = Query(None), language_id: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertSubtitle] @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, film_id, episode_id, language_id)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Subtitle data is incorrect")
    
    return {"message": "Subtitle inserted"}

@app.put("/subtitle/{id}")
async def update_subtitle(id: int, film_id: int = Query(...), episode_id: int = Query(...), language_id: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateSubtitle] @subtitle_id = ?, @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, id, film_id, episode_id, language_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Subtitle data is incorrect")

    return {"message": "Subtitle updated"}


@app.delete("/subtitle/{id}")
async def delete_subtitle(id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteSubtitle] @subtitle_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Subtitle data is incorrect")

    return {"message": "Subtitle deleted"}

#end subtitle

#start episode

@app.get("/episode/{data_type}")
async def get_episode(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectEpisode];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
        
    return correct_data.return_correct_format(result_list, data_type, "episode")

@app.get("/episode/{id}/{data_type}")
async def get_episode_by_id(id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectEpisodeById] @episode_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "episode")

@app.post("/episode")
async def insert_episode(series_id: int = Query(...), title: str = Query(...), duration: str = Query(...), episode_number: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertEpisode] @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, series_id, title, duration, episode_number)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Episode data is incorrect")
    
    return {"message": "Episode inserted"}


@app.put("/episode/{id}")
async def update_episode(id: int, series_id: int = Query(...), title: str = Query(...), duration: str = Query(...), episode_number: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateEpisode] @episode_id = ?, @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, id, series_id, title, duration, episode_number)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Episode data is incorrect")

    return {"message": "Episode updated"}

@app.delete("/episode/{id}")
async def delete_episode(id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteEpisode] @episode_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Episode data is incorrect")

    return {"message": "Episode deleted"}

#end episode

#start episode-dubbing view

@app.get("/episode-dubbing/{data_type}")
async def get_view_episode_dubbing(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodeDubbing];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "episode-dubbing-view")

@app.get("/episode-subtitle/{data_type}")
async def get_view_episode_subtitle(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodeSubtitle];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "episode-subtitle-view")

@app.get("/series-episodes/{data_type}")
async def get_view_series_episodes(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodesPerSeries];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "series-episodes-view")

@app.get("/film-attribute/{data_type}")
async def get_view_film_attribute(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmAttribute];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-attribute-view")

@app.get("/film-dubbing/{data_type}")
async def get_view_film_dubbing(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmDubbing];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-dubbing-view")

@app.get("/film-quality/{data_type}")
async def get_view_film_quality(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmQuality];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-quality-view")

@app.get("/film-subtitle/{data_type}")
async def get_view_film_quality(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmSubtitle];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-subtitle-view")

@app.get("/profile-watchlist-film/{data_type}")
async def get_view_profile_watchlist_film(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewProfileWatchlistFilm];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "profile-watchlist-film-view")

@app.get("/profile-watchlist-series/{data_type}")
async def get_view_profile_watchlist_series(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewProfileWatchlistSeries];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "profile-watchlist-series-view")

# @app.get("/profile-watchlist-all/{data_type}")

@app.get("/profile-preferred-attribute/{data_type}")
async def get_view_profile_preferred_attribute(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewProfilePreferredAttribute];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "profile_preferred_attribute-view")

@app.get("/series-genre/{data_type}")
async def get_view_series_genre(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewSeriesGenre];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "series-genre-view")

@app.get("/user-information/{data_type}")
async def get_view_user_information(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewUserInformation];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "user-information-view")

#dbms error
@app.get("/user-profile/{data_type}")
async def get_view_user_profile(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewUserProfile];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "user-profile-view")

@app.get("/episode-view/{data_type}")
async def get_view_episode_view(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodeView];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "view-episode-view")

@app.get("/film-view/{data_type}")
async def get_view_film_view(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmView];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "view-film-view")


def end_scope():
    pass

#start view
@app.get("/profile-film-overview/{view_id}/{profile_id}/{data_type}")
def get_view_profile_film_overview(view_id: int, profile_id: str, data_type: str, film_id: int = Query(None), episode_id: int = Query(None), token: str = Depends(oauth2_scheme)):
    id_to_paste = None

#start preferred attributes

@app.get("/preferred-attribute/{data_type}")
async def get_preferred_attribute(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectPreferredAttribute];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "preferred-attribute")

@app.get("/preferred-attribute/{profile_id}/{data_type}")
async def get_preferred_attribute_by_profile_id(profile_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectPreferredAttributeByProfileId] @profile_id = {profile_id};")
    rows = cursor.fetchall()
    result_list = []

    if not rows:
        raise HTTPException(status_code=404, detail="Profile not found")

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "preferred-attribute")

@app.post("/preferred-attribute")
async def insert_preferred_attribute(profile_id: int = Query(...), attribute_id: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertPreferredAttribute] @profile_id = ?, @attribute_id = ?;"
        cursor.execute(query, profile_id, attribute_id)
        conn.commit()

    except pyodbc.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"IntegrityError occurred: {e}")

    return {"message": "Preferred attribute inserted"}

@app.put("/preferred-attribute/{profile_id}-{attribute_id}")
async def update_preferred_attributes(profile_id: int, attribute_id: int, new_profile_id: int = Query(...), new_attribute_id: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdatePreferredAttribute] @profile_id = ?, @attribute_id = ?, @new_profile_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, profile_id, attribute_id, new_profile_id, new_attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Preferred attributes naming is incorrect")

    return {"message": "Preferred attribute updated"}

@app.delete("/preferred-attribute/{profile_id}-{attribute_id}")
async def delete_preferred_attribute(profile_id: int, attribute_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeletePreferredAttribute] @profile_id = ?, @attribute_id = ?;"
        cursor.execute(query, profile_id, attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Preferred attributes naming is incorrect")

    return {"message": "Preferred attribute deleted"}

#end preferred attributes

#start film genre

@app.get("/film-genre/{data_type}")
async def get_film_genre(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectFilmGenre];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-genre")

@app.get("/film-genre/{film_id}/{data_type}")
async def get_film_genre_by_film_id(film_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectFilmGenreByFilmId] @film_id = {film_id};")
    rows = cursor.fetchall()
    result_list = []

    if not rows:
        raise HTTPException(status_code=404, detail="Film not found")

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-genre")


@app.get("/genre-film/{attribute_id}/{data_type}")
async def get_film_genre_by_attribute_id(attribute_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectFilmGenreByAttributeId] @attribute_id = {attribute_id};")
    rows = cursor.fetchall()
    result_list = []

    if not rows:
        raise HTTPException(status_code=404, detail="Genre not found")

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-genre")

@app.post("/film-genre")
async def insert_film_genre(film_id: int = Query(...), attribute_id: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertFilmGenre] @film_id = ?, @attribute_id = ?;"
        cursor.execute(query, film_id, attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid input. Input should be integer.")

    return {"message": "Film genre inserted"}

@app.put("/film-genre/{film_id}-{attribute_id}")
async def update_preferred_attributes(film_id: int, attribute_id: int, new_film_id: int = Query(...), new_attribute_id: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdateFilmGenre] @film_id = ?, @attribute_id = ?, @new_film_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, film_id, attribute_id, new_film_id, new_attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film genre naming is incorrect")

    return {"message": "Film genre updated"}

@app.delete("/film-genre/{film_id}-{attribute_id}")
async def delete_preferred_attribute(film_id: int, attribute_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteFilmGenre] @film_id = ?, @attribute_id = ?;"
        cursor.execute(query, film_id, attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Preferred attributes naming is incorrect")

    return {"message": "Film genre deleted"}

#end film genre

#start series genre

@app.get("/series-genre/{data_type}")
async def get_series_genre(data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectSeriesGenre];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "series-genre")


@app.get("/series-genre/{series_id}/{data_type}")
async def get_series_genre_by_series_id(series_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectSeriesGenreBySeriesId] @series_id = {series_id};")
    rows = cursor.fetchall()
    result_list = []

    if not rows:
        raise HTTPException(status_code=404, detail="Series not found")

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "series-genre")


@app.get("/genre-series/{attribute_id}/{data_type}")
async def get_series_genre_by_attribute_id(attribute_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectSeriesGenreByAttributeId] @attribute_id = {attribute_id};")
    rows = cursor.fetchall()
    result_list = []

    if not rows:
        raise HTTPException(status_code=404, detail="Genre not found")

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "series-genre")


@app.post("/series-genre")
async def insert_series_genre(series_id: int = Query(...), attribute_id: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertSeriesGenre] @series_id = ?, @attribute_id = ?;"
        cursor.execute(query, series_id, attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid input. Input should be integer.")

    return {"message": "Series genre inserted"}


@app.put("/series-genre/{series_id}-{attribute_id}")
async def update_series_genre(series_id: int, attribute_id: int, new_series_id: int = Query(...),
                                      new_attribute_id: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdateSeriesGenre] @series_id = ?, @attribute_id = ?, @new_series_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, series_id, attribute_id, new_series_id, new_attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Series genre naming is incorrect")

    return {"message": "Series genre updated"}


@app.delete("/series-genre/{series_id}-{attribute_id}")
async def delete_series_genre(series_id: int, attribute_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteSeriesGenre] @series_id = ?, @attribute_id = ?;"
        cursor.execute(query, series_id, attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Series genre naming is incorrect")

    return {"message": "Series genre deleted"}

# end series genre

#start film quality

@app.get("/profile-film-overview/{view_id}/{profile_id}/{data_type}")
def get_view_profile_film_overview(view_id: int, profile_id: str, data_type: str, film_id: int = Query(None), episode_id: int = Query(None), token: str = Depends(oauth2_scheme)):
    id_to_paste = None

    correct_data.validate_data_type(data_type)

    decode_token(token)

    params_dict = {'film_id': film_id, 'episode_id': episode_id}

    for name, value in params_dict.items():
        if value is not None:
            id_to_paste = value
            variable_name = name
            break

    cursor.execute(f"EXEC [SelectViewProfileFilmOverview] @view_id = {view_id}, @profile_id = {profile_id}, @variable_name = {variable_name}, @id_to_paste = {id_to_paste};")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description): 
            if column[0] == "date":
                user_dict[column[0]] = str(row[idx])
            else:
                user_dict[column[0]] = row[idx]
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "profile-film-overview-view")

@app.get("/profile-film-overview/{data_type}")
def get_view_profile_film_overview_all(data_type: str, token: str = Depends(oauth2_scheme)):
    cursor.execute(f"EXEC [SelectFilmQuality];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "film-quality")


@app.get("/film-quality/{film_id}/{data_type}")
async def get_film_quality_by_film_id(film_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectFilmQualityByFilmId] @film_id = {film_id};")
    rows = cursor.fetchall()
    result_list = []

    if not rows:
        raise HTTPException(status_code=404, detail="Film not found")

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "series-genre")


@app.get("/quality-film/{quality_id}/{data_type}")
async def get_film_quality_by_quality_id(quality_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewProfileFilmOverviewAll];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            if column[0] == "date":
                user_dict[column[0]] = str(row[idx])
            else:
                user_dict[column[0]] = row[idx]
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "profile-film-overview-view")


#cats

@app.get("/cat-facts/")
async def get_axoloti_onfo(token: str = Depends(oauth2_scheme)):
    data_facts = []
    decode_token(token)

    response = requests.get("https://cat-fact.herokuapp.com/facts")

    soup = BeautifulSoup(response.text, 'html.parser')

    text_content = soup.get_text()
    data = json.loads(text_content)
    for i in data:
        data_facts.append({"fact": i["text"]})

    data_facts.append({"status code": response.status_code})

    return data_facts


@app.get("/quality-film/{quality_id}/{data_type}")
async def get_film_quality_by_quality_id(quality_id: int, data_type: str, token: str = Depends(oauth2_scheme)):
    correct_data.validate_data_type(data_type)

    decode_token(token)

    cursor.execute(f"EXEC [SelectFilmQualityByQualityId] @quality_id = {quality_id};")
    rows = cursor.fetchall()
    result_list = []

    if not rows:
        raise HTTPException(status_code=404, detail="Genre not found")

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return correct_data.return_correct_format(result_list, data_type, "series-genre")


@app.post("/film-quality")
async def insert_film_quality(film_id: int = Query(...), quality_id: int = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertFilmQuality] @film_id = ?, @quality_id = ?;"
        cursor.execute(query, film_id, quality_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid input. Input should be integer.")

    return {"message": "Film quality inserted"}


@app.put("/film-quality/{film_id}-{quality_id}")
async def update_film_quality(film_id: int, quality_id: int, new_film_id: int = Query(...),
                                      new_quality_id: str = Query(...), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdateFilmQuality] @film_id = ?, @quality_id = ?, @new_film_id = ?, @new_quality_id = ?;"
        cursor.execute(query, film_id, quality_id, new_film_id, new_quality_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film quality naming is incorrect")

    return {"message:" "Film quality updated"}


@app.delete("/film-quality/{film_id}-{quality_id}")
async def delete_film_quality(film_id: int, quality_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [DeleteFilmQuality] @film_id = ?, @quality_id = ?;"
        cursor.execute(query, film_id, quality_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film quality naming is incorrect")

    return {"message": "Film quality deleted"}

# end film quality

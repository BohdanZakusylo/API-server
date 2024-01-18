import os
import pyodbc
import hashlib
import requests
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, Depends, Header
from app.token_generator.token_validation import encode_token, decode_token, encode_refresh_token, decode_refresh_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.data_type_validation.data_validate import Correct_Data
from bs4 import BeautifulSoup
from datetime import datetime
from app.base_classes.base_classes import BaseModels
from typing import Optional


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
    return {"message": "Hello World", "status_code": 200, "message": "OK"}


@app.post("/registration")
async def registration(registration_info: BaseModels.RegistrationIngfo):
    try:
        query = """EXECUTE [InsertUser] @email = ?, @password = ?, @username = ?, @age = ?;"""
        password_bytes = registration_info.password.encode('utf-8')
        hashed_password = hashlib.sha256(password_bytes).hexdigest()
        cursor.execute(query, registration_info.email, hashed_password, registration_info.username, registration_info.age)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Username and email should be unique")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="Username and email should be unique")

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].email = '{registration_info.email}';")

    id = cursor.fetchone()[0]

    return {
        "token": encode_token(id, registration_info.username)
    }

@app.get("/login")
async def login(login_info: BaseModels.LoginInfo):
    try:
        query = """SELECT [user].user_id FROM [user] WHERE [user].email = ? AND [user].password = ?;"""
        password = login_info.password.encode('utf-8')
        hashed_password_bytes = hashlib.sha256(password).digest()
        print(hashed_password_bytes)
        cursor.execute(query, login_info.email, hashed_password_bytes)
        user_id = cursor.fetchone()[0]
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "token": encode_token(user_id, login_info.email)
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

#start attributes

@app.get("/attributes")
async def get_attributes(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)
    
    cursor.execute(f"EXEC [SelectAtribute];")
    rows = cursor.fetchall()
    result_list = []

    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "attributes")

@app.get("/attributes/{id}")
async def get_attributes_by_id(id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):

    decode_token(token)

    cursor.execute(f"EXEC [SelectAttributeById] @attribute_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}


    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "attributes")

@app.post("/attributes")
async def insert_atributes(attribute_data: BaseModels.AttributesInfo, token: str = Depends(oauth2_scheme)):

    decode_token(token)
    
    try:
        query = f"EXEC [InsertAttribute] @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, attribute_data.attribute_type, attribute_data.attribute_description)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Attributes name is incorrect")
    
    return {"message": "Atribute inserted"}

@app.put("/attributes/{id}")
async def update_attributes(id: int, attribute_info: BaseModels.AttributesInfo, token: str = Depends(oauth2_scheme)):

    decode_token(token)

    try: 
        query = f"EXEC [UpdateAttribute] @attribute_id = ?, @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, id, attribute_info.attribute_type, attribute_info.attribute_description)
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

@app.get("/language")
async def get_languages(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    
    decode_token(token)
    
    cursor.execute(f"EXEC [SelectLanguage];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}


    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "languages")


@app.get("/language/{id}")
async def get_languages_by_id(id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    
    decode_token(token)

    cursor.execute(f"EXEC [SelectLanguageById] @language_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "languages")

@app.post("/language")
async def insert_languages(language_info: BaseModels.LanguageInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)
        
    try:
        query = f"EXEC [InsertLanguage] @language_name = ?;"
        cursor.execute(query, language_info.language_name)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Language name is incorrect")

    return {"message": "Language inserted"}

@app.put("/language/{id}")
async def update_languages(id: int, language_info: BaseModels.LanguageInfo, token: str = Depends(oauth2_scheme)):

    decode_token(token)

    try: 
        query = f"EXEC [UpdateLanguage] @language_id = ?, @language_name = ?;"
        cursor.execute(query, id, language_info.language_name)
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

@app.get("/profile")
async def get_profile(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    
    decode_token(token)
    
    cursor.execute(f"EXEC [SelectProfile];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile")

@app.get("/profile/{id}")
async def get_profile_by_id(id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectProfileById] @profile_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile")


@app.post("/profile")
async def insert_profile(profile_info: BaseModels.ProfileInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)
    print(profile_info.user_id, profile_info.age, profile_info.nick_name, profile_info.profile_picture)
    try:
        query = f"EXEC [InsertProfile] @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, profile_info.user_id, profile_info.age, profile_info.nick_name, profile_info.profile_picture)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Profile data is incorrect")
    
    return {"message": "Profile inserted"}


@app.put("/profile/{id}")
async def update_profile(id: int, profile_info: BaseModels.ProfileInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateProfile] @profile_id = ?, @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, id, profile_info.user_id, profile_info.age, profile_info.nick_name, profile_info.profile_picture)
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

@app.get("/film")
async def get_film(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectFilm];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film")


@app.get("/film/{id}")
async def get_film_by_id(id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film")

@app.post("/film")
async def insert_film(film_info: BaseModels.FilmInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertFilm] @title = ?, @duration = ?;"
        cursor.execute(query, film_info.title, film_info.duration)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film data is incorrect")
    
    return {"message": "Film inserted"}

@app.put("/film/{id}")
async def update_film(id: int, film_info: BaseModels.FilmInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateFilm] @film_id = ?, @title = ?, @duration = ?;"
        cursor.execute(query, id, film_info.title, film_info.duration)
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

@app.get("/quality")
async def get_quality(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    
    
    decode_token(token)
    
    cursor.execute(f"EXEC [SelectQuality];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "quality")

@app.get("/quality/{id}")
async def get_quality_by_id(id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    
    
    decode_token(token)

    cursor.execute(f"EXEC [SelectQualityById] @quality_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "quality")

@app.post("/quality")
async def insert_quality(quality_info: BaseModels.QualityInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertQuality] @quality_type = ?;"
        cursor.execute(query, quality_info.quality_type)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Quality data is incorrect")
    
    return {"message": "Quality inserted"}


@app.put("/quality/{id}")
async def update_quality(id: int, quality_info: BaseModels.QualityInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateQuality] @quality_id = ?, @quality_type = ?;"
        cursor.execute(query, id, quality_info.quality_type)
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

@app.get("/subtitle")
async def get_subtitle(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectSubtitle];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subtitle")

@app.get("/subtitle/{id}")
async def get_subtitle_by_id(id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectSubtitleById] @subtitle_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subtitle")

@app.post("/subtitle")
async def insert_subtitle(subtitle_info: BaseModels.SubtitleInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertSubtitle] @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, subtitle_info.film_id, subtitle_info.episode_id, subtitle_info.language_id)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Subtitle data is incorrect")
    
    return {"message": "Subtitle inserted"}

@app.put("/subtitle/{id}")
async def update_subtitle(id: int, subtitle_info: BaseModels.SubtitleInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateSubtitle] @subtitle_id = ?, @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, id, subtitle_info.film_id, subtitle_info.episode_id, subtitle_info.language_id)
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

@app.get("/episode")
async def get_episode(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)
    
    cursor.execute(f"EXEC [SelectEpisode];")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "episode")

@app.get("/episode/{id}")
async def get_episode_by_id(id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectEpisodeById] @episode_id = {id};")
    rows = cursor.fetchall()
    result_list = []
    
    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "episode")

@app.post("/episode")
async def insert_episode(episode_info: BaseModels.EpisodeInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertEpisode] @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, episode_info.series_id, episode_info.title, episode_info.duration, episode_info.episode_number)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Episode data is incorrect")
    
    return {"message": "Episode inserted"}


@app.put("/episode/{id}")
async def update_episode(id: int, episode_info: BaseModels.EpisodeInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateEpisode] @episode_id = ?, @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, id, episode_info.series_id, episode_info.title, episode_info.duration, episode_info.episode_number)
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

@app.get("/episode-dubbing")
async def get_view_episode_dubbing(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodeDubbing];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "episode-dubbing-view")

@app.get("/episode-subtitle")
async def get_view_episode_subtitle(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodeSubtitle];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "episode-subtitle-view")

@app.get("/series-episodes")
async def get_view_series_episodes(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodesPerSeries];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-episodes-view")

@app.get("/film-attribute")
async def get_view_film_attribute(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmAttribute];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-attribute-view")

@app.get("/film-dubbing")
async def get_view_film_dubbing(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmDubbing];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-dubbing-view")

@app.get("/film-quality")
async def get_view_film_quality(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmQuality];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-quality-view")

@app.get("/film-subtitle")
async def get_view_film_quality(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmSubtitle];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-subtitle-view")

@app.get("/profile-watchlist-film")
async def get_view_profile_watchlist_film(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewProfileWatchlistFilm];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile-watchlist-film-view")

@app.get("/profile-watchlist-series")
async def get_view_profile_watchlist_series(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewProfileWatchlistSeries];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile-watchlist-series-view")

# @app.get("/profile-watchlist-all")

@app.get("/profile-preferred-attribute")
async def get_view_profile_preferred_attribute(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewProfilePreferredAttribute];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile_preferred_attribute-view")

@app.get("/series-genre")
async def get_view_series_genre(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewSeriesGenre];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre-view")

@app.get("/user-information")
async def get_view_user_information(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewUserInformation];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user-information-view")

#dbms error
@app.get("/user-profile")
async def get_view_user_profile(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewUserProfile];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user-profile-view")

@app.get("/episode-view")
async def get_view_episode_view(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewEpisodeView];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "view-episode-view")

@app.get("/film-view")
async def get_view_film_view(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectViewFilmView];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "view-film-view")

#start preferred attributes

@app.get("/preferred-attribute")
async def get_preferred_attribute(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectPreferredAttribute];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "preferred-attribute")

@app.get("/preferred-attribute/{profile_id}")
async def get_preferred_attribute_by_profile_id(profile_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "preferred-attribute")

@app.post("/preferred-attribute")
async def insert_preferred_attribute(preferred_attribute_info: BaseModels.PreferredAttributeInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertPreferredAttribute] @profile_id = ?, @attribute_id = ?;"
        cursor.execute(query, preferred_attribute_info.profile_id, preferred_attribute_info.attribute_id)
        conn.commit()

    except pyodbc.IntegrityError as e:
        raise HTTPException(status_code=400, detail=f"IntegrityError occurred: {e}")

    return {"message": "Preferred attribute inserted"}

@app.put("/preferred-attribute/{profile_id}-{attribute_id}")
async def update_preferred_attributes(profile_id: int, attribute_id: int, preferred_attribute_info: BaseModels.PreferredAttributeInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdatePreferredAttribute] @profile_id = ?, @attribute_id = ?, @new_profile_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, profile_id, attribute_id, preferred_attribute_info.new_profile_id, preferred_attribute_info.new_attribute_id)
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

@app.get("/film-genre")
async def get_film_genre(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectFilmGenre];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-genre")

@app.get("/film-genre/{film_id}")
async def get_film_genre_by_film_id(film_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-genre")


@app.get("/genre-film/{attribute_id}")
async def get_film_genre_by_attribute_id(attribute_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-genre")

@app.post("/film-genre")
async def insert_film_genre(film_genre_info: BaseModels.FilmGenreInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertFilmGenre] @film_id = ?, @attribute_id = ?;"
        cursor.execute(query, film_genre_info.film_id, film_genre_info.attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid input. Input should be integer.")

    return {"message": "Film genre inserted"}

@app.put("/film-genre/{film_id}-{attribute_id}")
async def update_preferred_attributes(film_id: int, attribute_id: int, film_genre_info: BaseModels.FilmGenreInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdateFilmGenre] @film_id = ?, @attribute_id = ?, @new_film_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, film_id, attribute_id, film_genre_info.new_film_id, film_genre_info.new_attribute_id)
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

@app.get("/series-genre")
async def get_series_genre(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

    decode_token(token)

    cursor.execute(f"EXEC [SelectSeriesGenre];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")


@app.get("/series-genre/{series_id}")
async def get_series_genre_by_series_id(series_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")


@app.get("/genre-series/{attribute_id}")
async def get_series_genre_by_attribute_id(attribute_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")


@app.post("/series-genre")
async def insert_series_genre(series_genre_info: BaseModels.SeriesGenerInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertSeriesGenre] @series_id = ?, @attribute_id = ?;"
        cursor.execute(query, series_genre_info.series_id, series_genre_info.attribute_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid input. Input should be integer.")

    return {"message": "Series genre inserted"}


@app.put("/series-genre/{series_id}-{attribute_id}")
async def update_series_genre(series_id: int, attribute_id: int, series_genre_info: BaseModels.SeriesGenerInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdateSeriesGenre] @series_id = ?, @attribute_id = ?, @new_series_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, series_id, attribute_id, series_genre_info.new_series_id, series_genre_info.new_attribute_id)
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
@app.get("/profile-film-overview/{view_id}/{profile_id}")
def get_view_profile_film_overview(view_id: int, profile_id: str, accept: str = Header(default="application/json"), film_id: int = Query(None), episode_id: int = Query(None), token: str = Depends(oauth2_scheme)):
    id_to_paste = None

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile-film-overview-view")

@app.get("/profile-film-overview")
def get_view_profile_film_overview_all(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    cursor.execute(f"EXEC [SelectFilmQuality];")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-quality")


@app.get("/film-quality/{film_id}")
async def get_film_quality_by_film_id(film_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")


@app.get("/quality-film/{quality_id}")
async def get_film_quality_by_quality_id(quality_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    
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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile-film-overview-view")


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

#start film quality

@app.get("/quality-film/{quality_id}")
async def get_film_quality_by_quality_id(quality_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    

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
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")

@app.post("/film-quality")
async def insert_film_quality(film_quality_info: BaseModels.FilmQualityInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [InsertFilmQuality] @film_id = ?, @quality_id = ?;"
        cursor.execute(query, film_quality_info.film_id, film_quality_info.quality_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid input. Input should be integer.")

    return {"message": "Film quality inserted"}


@app.put("/film-quality/{film_id}-{quality_id}")
async def update_film_quality(film_id: int, quality_id: int, film_quality_info: BaseModels.FilmQualityInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = f"EXEC [UpdateFilmQuality] @film_id = ?, @quality_id = ?, @new_film_id = ?, @new_quality_id = ?;"
        cursor.execute(query, film_id, quality_id, film_quality_info.new_film_id, film_quality_info.new_quality_id)
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

#Users start
@app.get("/users")
async def get_users(accept: str = Header(default="application/json"), token: str =  Depends(oauth2_scheme)):

    decode_token(token)

    cursor.execute(f"EXECUTE SelectUser;")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user")

@app.get("/users/{id}")
async def get_users_by_id(id: int, accept: str = Header(default="application/json"), token: str =  Depends(oauth2_scheme)):
    decode_token(token)

    cursor.execute(f"EXECUTE SelectUserById @user_id = {id};")
    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user")

@app.put("/users/{id}")
async def put_users(id: int, update_user_info: BaseModels.UpdateUserInfo, token: str = Depends(oauth2_scheme)):
    #TODO check if user wants to update itself
    decode_token(token)

    try:

        query = """EXECUTE UpdateUser @user_id = ?, @username = ?, @language_id = ?, @password = ?, @is_activated = ?, @is_blocked = ?, @email = ?;"""
        cursor.execute(query, id, update_user_info.username, update_user_info.language_id, update_user_info.password, update_user_info.is_activated, update_user_info.is_blocked, update_user_info.login_info.email)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Email should be unique")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute(f"EXECUTE SelectUserById @user_id = {id};")

    id = cursor.fetchone()[0]

    return {
        "token": encode_token(id, update_user_info.username)
    }

@app.delete("/users/{id}")
async def delete_users(id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE DeleteUser @user_id = ?;"""
        cursor.execute(query, id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Email should be unique")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="User not found")

    return f"User with id = {id} deleted successfully."

#Users end

#Dubbing start

@app.get("/dubbings")
async def get_dubbings(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectDubbing;"""
    cursor.execute(query)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "dubbing")

@app.get("/dubbings/{dubbing_id}")
async def get_dubbings_by_id(dubbing_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectDubbingById @dubbing_id = ?;"""
    cursor.execute(query, dubbing_id)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "dubbing")

@app.post("/dubbings")
async def post_dubbings(dubbing_info: BaseModels.DubbingInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    if (dubbing_info.film_id is None and dubbing_info.episode_id is None) or (dubbing_info.film_id is not None and dubbing_info.episode_id is not None):
        raise HTTPException(status_code=400, detail="Wrong input")

    query = """EXECUTE InsertDubbing @film_id = ?, @episode_id = ?, @language_id = ?, @dubbing_company = ?;"""
    cursor.execute(query, dubbing_info.film_id, dubbing_info.episode_id, dubbing_info.language_id, dubbing_info.dubbing_company)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return "Dubbing added successfully."

@app.put("/dubbings/{dubbing_id}")
async def put_dubbings(dubbing_id: int, dubbing_info: BaseModels.DubbingInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE UpdateDubbing @dubbing_id = ?, @film_id = ?, @episode_id = ?, @language_id = ?, @dubbing_company = ?;"""
    cursor.execute(query, dubbing_id, dubbing_info.film_id, dubbing_info.episode_id, dubbing_info.language_id, dubbing_info.dubbing_company)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Dubbing with id = {dubbing_id} edited successfully."

@app.delete("/dubbings/{dubbing_id}")
async def delete_dubbings(dubbing_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE DeleteDubbing @dubbing_id = ?;"""
    cursor.execute(query, dubbing_id)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Dubbing with id = {dubbing_id} deleted successfully."

#Dubbing end

#Series start

@app.get("/series")
async def get_series(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectSeries;"""
    cursor.execute(query)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series")

@app.get("/series/{series_id}")
async def get_series_by_id(series_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectSeriesById @series_id = ?;"""
    cursor.execute(query, series_id)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series")

@app.post("/series")
async def post_series(series_info: BaseModels.SeriesInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE InsertSeries @title = ?, @episodeAmount = ?;"""
    cursor.execute(query, series_info.title, series_info.episode_amount)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return "Series added successfully."

@app.put("/series/{series_id}")
async def put_series(series_id: int, series_info: BaseModels.SeriesInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE UpdateSeries @series_id = ?, @title = ?, @episodeAmount = ?;"""
    cursor.execute(query, series_id, series_info.title, series_info.episode_amount)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Series with id = {series_id} edited successfully."

@app.delete("/series/{series_id}")
async def delete_series(series_id: int, token: str = Depends(oauth2_scheme)):

    decode_token(token)

    query = """EXECUTE DeleteSeries @series_id = ?;"""
    cursor.execute(query, series_id)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Series with id = {series_id} deleted successfully."

#Series end

#Subscription start

@app.get("/subscriptions")
async def get_subscriptions(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectSubscription;"""
    cursor.execute(query)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subscription")

#TODO fix all other routes done by vlad
@app.get("/subscriptions/{subscription_id}")
async def get_subscriptions_by_id(subscription_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectSubscriptionById @subscription_id = ?;"""
    cursor.execute(query, subscription_id)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subscription")

@app.post("/subscriptions")
async def post_subscriptions(subscription_info: BaseModels.SubscriptionInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE InsertSubscription @user_id = ?, @type = ?, @price = ?, @start_date = ?, @expiration_date = ?, @is_discount = ?;"""
    cursor.execute(query, subscription_info.user_id, subscription_info.type, subscription_info.price, subscription_info.start_date, subscription_info.expiration_date, subscription_info.is_discount)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return "Subscription added successfully."

@app.put("/subscriptions/{subscription_id}")
async def put_subscriptions(subscription_id: int, subscription_info: BaseModels.SubscriptionInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE UpdateSubscription @subscription_id = ?, @user_id = ?, @type = ?, @price = ?, @start_date = ?, @expiration_date = ?, @is_discount = ?;"""
    cursor.execute(query, subscription_id, subscription_info.user_id, subscription_info.type, subscription_info.price, subscription_info.start_date, subscription_info.expiration_date, subscription_info.is_discount)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Subscription with id = {subscription_id} edited successfully."

@app.delete("/subscriptions/{subscription_id}")
async def delete_subscriptions(subscription_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE DeleteSubscription @subscription_id = ?;"""
    cursor.execute(query, subscription_id)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Subscription with id = {subscription_id} deleted successfully."

#Subscription end

#Watchlist start

@app.get("/watchlists")
async def get_watchlists(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectWatchlist_Item;"""
    cursor.execute(query)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "watchlist_item")

@app.get("/watchlists/{watchlist_item_id}")
async def get_watchlists_by_id(watchlist_item_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    query = """EXECUTE SelectWatchlist_ItemById @watchlist_item_id = ?;"""
    cursor.execute(query, watchlist_item_id)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)
    response = {"status": "200 OK", "data": result_list}

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subscription")

@app.post("/watchlists")
async def post_watchlist_item(watchlist_item_info: BaseModels.WatchlistItemInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)
    if (watchlist_item_info.film_id is None and watchlist_item_info.series_id is None) or (watchlist_item_info.film_id is not None and watchlist_item_info.series_id is not None):
        raise HTTPException(status_code=400, detail="Wrong input")

    query = """EXECUTE InsertWatchlist_Item @profile_id = ?, @series_id = ?, @film_id = ?, @is_finished = ?;"""
    cursor.execute(query, watchlist_item_info.profile_id, watchlist_item_info.series_id, watchlist_item_info.film_id, watchlist_item_info.is_finished)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return "Watchlist item added successfully."

@app.put("/watchlists/{watchlist_item_id}")
async def put_series(watchlist_item_id: int, watchlist_item_info: BaseModels.WatchlistItemInfo, token: str = Depends(oauth2_scheme)):

    if (watchlist_item_info.film_id is None and watchlist_item_info.series_id is None) or (watchlist_item_info.film_id is not None and watchlist_item_info.series_id is not None):
        raise HTTPException(status_code=400, detail="Wrong input")

    decode_token(token)

    query = """EXECUTE UpdateWatchlist_Item @watchlist_item_id = ?, @profile_id = ?, @series_id = ?, @film_id = ?, @is_finished = ?;"""
    cursor.execute(query, watchlist_item_id, watchlist_item_info.profile_id, watchlist_item_info.series_id, watchlist_item_info.film_id, watchlist_item_info.is_finished)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Watchlist item with id = {watchlist_item_id} edited successfully."

@app.delete("/watchlists/{watchlist_item_id}")
async def delete_series(watchlist_item_id: int, token: str = Depends(oauth2_scheme)):

    decode_token(token)

    query = """EXECUTE DeleteWatchlist_Item @watchlist_item_id = ?;"""
    cursor.execute(query, watchlist_item_id)
    conn.commit()

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Watchlist item with id = {watchlist_item_id} deleted successfully."

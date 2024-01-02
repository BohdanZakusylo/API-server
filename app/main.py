import os
import pyodbc
import hashlib
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from app.token_generator.token_validation import encode_token, decode_token, encode_refresh_token, decode_refresh_token
from app.data_type_validation.data_validate import Correct_Data
from datetime import datetime
from app.base_classes.login_info import LoginInfo
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
async def login(login_info: LoginInfo):
    try:
        query = """EXECUTE [InsertUser] @email = ?, @password = ?, @username = ?, @age = ?;"""
        password_bytes = login_info.password.encode('utf-8')
        hashed_password = hashlib.sha256(password_bytes).hexdigest()
        cursor.execute(query, login_info.email, hashed_password, login_info.username, login_info.age)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Email should be unique")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].email = '{login_info.email}';")

    id = cursor.fetchone()[0]

    return {
        "token": encode_token(id, login_info.username)
    }

@app.get("/refresh-token")
def get_refresh_token_by_token(token: str = Query(...)):
    decoded_token = decode_token(token)
    

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].user_id = {decoded_token['id']};")

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "refresh_token": encode_refresh_token(decoded_token["id"], decoded_token["username"]),
    }


@app.get("/new-token")
def get_token_by_refresh_token(refresh_token: str = Query(...)):
    decoded_token = decode_refresh_token(refresh_token)

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].user_id = {decoded_token['id']};")

    if cursor.fetchone() is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "token": encode_token(decoded_token["id"], decoded_token["username"]),
    }

#start atributes

@app.get("/atributes/{data_type}")
async def get_atributes(data_type: str, token : str = Query(...)):
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
async def get_atributes_by_id(id: int, data_type: str, token : str = Query(...)):
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
async def insert_atributes(attribute_type: str = Query(...), attribute_description: str = Query(...), token : str = Query(...)):

    decode_token(token)
    
    try:
        query = f"EXEC [InsertAttribute] @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, attribute_type, attribute_description)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Attributes name is incorrect")
    
    return {"message": "Atribute inserted"}

@app.put("/atributes/{id}")
async def update_attributes(id: int, attribute_type: str = Query(...), attribute_description: str = Query(...), token : str = Query(...)):

    decode_token(token)

    try: 
        query = f"EXEC [UpdateAttribute] @attribute_id = ?, @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, id, attribute_type, attribute_description)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Attributes naming is incorrect")

    return {"message": "Atribute updated"}

@app.delete("/atributes/{id}")
async def delete_attributes(id: int, token : str = Query(...)):

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
async def get_languages(data_type: str, token : str = Query(...)):
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
async def get_languages_by_id(id: int, data_type: str, token : str = Query(...)):
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
async def insert_languages(language_name: str = Query(...), token : str = Query(...)):
    decode_token(token)
        
    try:
        query = f"EXEC [InsertLanguage] @language_name = ?;"
        cursor.execute(query, language_name)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Language name is incorrect")

    return {"message": "Language inserted"}

@app.put("/language/{id}")
async def update_languages(id: int, language_name: str = Query(...), token : str = Query(...)):

    decode_token(token)

    try: 
        query = f"EXEC [UpdateLanguage] @language_id = ?, @language_name = ?;"
        cursor.execute(query, id, language_name)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Language naming is incorrect")

    return {"message": "Language updated"}

@app.delete("/language/{id}")
async def delete_languages(id: int, token : str = Query(...)):

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
async def get_profile(data_type: str, token : str = Query(...)):
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
async def get_profile_by_id(id: int, data_type: str, token : str = Query(...)):
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
async def insert_profile(user_id: int = Query(...), age: int = Query(...), nick_name: str = Query(...), profile_picture: str = Query(None), token : str = Query(...)):
    decode_token(token)
    
    try:
        query = f"EXEC [InsertProfile] @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, user_id, age, nick_name, profile_picture)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Profile data is incorrect")
    
    return {"message": "Profile inserted"}


@app.put("/profile/{id}")
async def update_profile(id: int, user_id: int = Query(...), age: int = Query(...), nick_name: str = Query(...), profile_picture: str = Query(None), token : str = Query(...)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateProfile] @profile_id = ?, @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, id, user_id, age, nick_name, profile_picture)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Profile data is incorrect")

    return {"message": "Profile updated"}

@app.delete("/profile/{id}")
async def delete_profile(id: int, token : str = Query(...)):
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
async def get_film(data_type: str, token : str = Query(...)):
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
async def get_film_by_id(id: int, data_type: str, token : str = Query(...)):
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
async def insert_film(title: str = Query(...), duration: str = Query(...), token : str = Query(...)):
    decode_token(token)

    try:
        query = f"EXEC [InsertFilm] @title = ?, @duration = ?;"
        cursor.execute(query, title, duration)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film data is incorrect")
    
    return {"message": "Film inserted"}

@app.put("/film/{id}")
async def update_film(id: int, title: str = Query(...), duration: str = Query(...), token : str = Query(...)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateFilm] @film_id = ?, @title = ?, @duration = ?;"
        cursor.execute(query, id, title, duration)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Film data is incorrect")

    return {"message": "Film updated"}


@app.delete("/film/{id}")
async def delete_film(id: int, token : str = Query(...)):
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
async def get_quality(data_type: str, token : str = Query(...)):
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
async def get_quality_by_id(id: int, data_type: str, token : str = Query(...)):
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
async def insert_quality(quality_type: str = Query(...), token : str = Query(...)):
    decode_token(token)

    try:
        query = f"EXEC [InsertQuality] @quality_type = ?;"
        cursor.execute(query, quality_type)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Quality data is incorrect")
    
    return {"message": "Quality inserted"}


@app.put("/quality/{id}")
async def update_quality(id: int, quality_type: str = Query(...), token : str = Query(...)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateQuality] @quality_id = ?, @quality_type = ?;"
        cursor.execute(query, id, quality_type)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Quality data is incorrect")

    return {"message": "Quality updated"}


@app.delete("/quality/{id}")
async def delete_quality(id: int, token : str = Query(...)):
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
async def get_subtitle(data_type: str, token : str = Query(...)):
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
async def get_subtitle_by_id(id: int, data_type: str, token : str = Query(...)):
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
async def insert_subtitle(film_id: int = Query(None), episode_id: int = Query(None), language_id: int = Query(...), token : str = Query(...)):
    decode_token(token)

    try:
        query = f"EXEC [InsertSubtitle] @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, film_id, episode_id, language_id)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Subtitle data is incorrect")
    
    return {"message": "Subtitle inserted"}

@app.put("/subtitle/{id}")
async def update_subtitle(id: int, film_id: int = Query(...), episode_id: int = Query(...), language_id: int = Query(...), token : str = Query(...)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateSubtitle] @subtitle_id = ?, @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, id, film_id, episode_id, language_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Subtitle data is incorrect")

    return {"message": "Subtitle updated"}


@app.delete("/subtitle/{id}")
async def delete_subtitle(id: int, token : str = Query(...)):
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
async def get_episode(data_type: str, token : str = Query(...)):
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
async def get_episode_by_id(id: int, data_type: str, token : str = Query(...)):
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
async def insert_episode(series_id: int = Query(...), title: str = Query(...), duration: str = Query(...), episode_number: int = Query(...), token : str = Query(...)):
    decode_token(token)

    try:
        query = f"EXEC [InsertEpisode] @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, series_id, title, duration, episode_number)
        conn.commit()
    
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Episode data is incorrect")
    
    return {"message": "Episode inserted"}


@app.put("/episode/{id}")
async def update_episode(id: int, series_id: int = Query(...), title: str = Query(...), duration: str = Query(...), episode_number: int = Query(...), token : str = Query(...)):
    decode_token(token)

    try: 
        query = f"EXEC [UpdateEpisode] @episode_id = ?, @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, id, series_id, title, duration, episode_number)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Episode data is incorrect")

    return {"message": "Episode updated"}

@app.delete("/episode/{id}")
async def delete_episode(id: int, token : str = Query(...)):
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
async def get_view_episode_dubbing(data_type: str, token: str = Query(...)):
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
async def get_view_episode_subtitle(data_type: str, token: str = Query(...)):
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
async def get_view_series_episodes(data_type: str, token: str = Query(...)):
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
async def get_view_film_attribute(data_type: str, token: str = Query(...)):
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
async def get_view_film_dubbing(data_type: str, token: str = Query(...)):
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
async def get_view_film_quality(data_type: str, token: str = Query(...)):
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
async def get_view_film_quality(data_type: str, token: str = Query(...)):
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
async def get_view_profile_watchlist_film(data_type: str, token: str = Query(...)):
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
async def get_view_profile_watchlist_series(data_type: str, token: str = Query(...)):
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
async def get_view_profile_preferred_attribute(data_type: str, token: str = Query(...)):
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
async def get_view_series_genre(data_type: str, token: str = Query(...)):
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
async def get_view_user_information(data_type: str, token: str = Query(...)):
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
async def get_view_user_profile(data_type: str, token: str = Query(...)):
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
async def get_view_episode_view(data_type: str, token: str = Query(...)):
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
async def get_view_film_view(data_type: str, token: str = Query(...)):
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

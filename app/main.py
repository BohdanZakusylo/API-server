import os
import pyodbc
import hashlib
import requests
import json

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException, Depends, Header, status
from app.token_generator.token_validation import encode_token, decode_token, encode_refresh_token, decode_refresh_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.data_type_validation.data_validate import Correct_Data
from bs4 import BeautifulSoup
from app.base_classes.base_classes import BaseModels
from typing import Optional
from datetime import datetime


import app.connection as connection
import app.routers.login.login as login
import app.routers.attributes.attributes as attributes
import app.routers.languages.languages as languages
import app.routers.profiles.profiles as profiles
import app.routers.films.films as films
import app.routers.quality.quality as quality
import app.routers.subtitles.subtitles as subtitles
import app.routers.episodes.episodes as episodes
import app.routers.preferred_attributes.preffered_attribute as preferred_attributes
import app.routers.film_genre.film_genre as film_genre
import app.routers.views.views as views
import app.routers.series_genre.series_genre as series_genre
import app.routers.film_quality.film_quality as film_qaulity
import app.routers.users.users as users
import app.routers.dubbings.dubbings as dubbings
import app.routers.series.series as series
import app.routers.subscriptions.subscriptions as subscriptions
import app.routers.watchlists.watchlists as watchlists

correct_data = Correct_Data()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
conn, cursor = connection.conn, connection.cursor


app = FastAPI()
#other routers include
app.include_router(login.login_router)
app.include_router(attributes.attributes_router)
app.include_router(languages.languages_router)
app.include_router(profiles.profiles_router)
app.include_router(films.films_router)
app.include_router(quality.quality_router)
app.include_router(subtitles.subtitles_router)
app.include_router(episodes.episodes_router)
app.include_router(preferred_attributes.preferred_attributes_router)
app.include_router(film_genre.film_genre_router)
app.include_router(views.views_router)
app.include_router(series_genre.series_genre_router)
app.include_router(film_qaulity.film_quality_router)
app.include_router(users.users_router)
app.include_router(dubbings.dubbings_router)
app.include_router(series.series_router)
app.include_router(subscriptions.subscriptions_router)
app.include_router(watchlists.watchlists_router)


@app.get("/")
async def main_page():
    return {"message": "Hello World", "status_code": 200, "message": "OK"}


#start attributes


#end attributes

#start languages

#end languages

#start profile

#end profile

#start film

#end film

#start quality

#end quality

#start subtitle

#end subtitle

#start episode


#end episode

#start episode-dubbing view

#start preferred attributes

#end preferred attributes
#start film genre

#end film genre

#start series genre

# end series genre

#start film quality


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

# end film quality

#Users start
@app.get("/users")
async def get_users(accept: str = Header(default="application/json"), token: str =  Depends(oauth2_scheme)):
    decode_token(token)

    try:
        cursor.execute(f"EXECUTE SelectUser;")
        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}
    except pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user")

@app.get("/users/{id}")
async def get_users_by_id(id: int, accept: str = Header(default="application/json"), token: str =  Depends(oauth2_scheme)):
    decode_token(token)

    try:
        cursor.execute(f"EXECUTE SelectUserById @user_id = {id};")
        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user")

@app.put("/users/{id}", status_code=status.HTTP_200_OK)
async def put_users(id: int, update_user_info: BaseModels.UpdateUserInfo, token: str = Depends(oauth2_scheme)):
    #TODO check if user wants to update itself
    decode_token(token)

    try:

        query = """EXECUTE UpdateUser @user_id = ?, @username = ?, @language_id = ?, @password = ?, @is_activated = ?, @is_blocked = ?, @email = ?;"""
        cursor.execute(query, id, update_user_info.username, update_user_info.language_id, update_user_info.password, update_user_info.is_activated, update_user_info.is_blocked, update_user_info.login_info.email)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")

    except pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

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

    except pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=404, detail="User not found")

    return f"User with id = {id} deleted successfully."

#Users end

#Dubbing start

#Dubbing end

#Series start

#Series end

#Subscription start


#Subscription end

#Watchlist start

#Watchlist end

@app.get("/dubbings-languages/{language_id}")
async def get_dubbing_by_language_id(language_id: int, token: str = Query(...)):

    if decode_token(token) == "token is invalid":
        raise HTTPException(status_code=401, detail="token is invalid")

    try:
        query = """EXECUTE SelectDubbingByLanguageId @language_id = ?;"""
        cursor.execute(query, language_id)

    except pyodbc.IntegrityError as e:
        print(e)

    rows = cursor.fetchall()

    return len(rows)

@app.get("/registration-info")
async def get_registration_info(token: str = Query(...)):

    if decode_token(token) == "token is invalid":
        raise HTTPException(status_code=401, detail="token is invalid")

    try:

        query = """EXECUTE SelectRegistrationInfo;"""
        cursor.execute(query)

    except pyodbc.IntegrityError as e:
        print(e)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return result_list

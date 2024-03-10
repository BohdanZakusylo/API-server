import app.common as common
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

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr



correct_data = common.Correct_Data()

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")
conn, cursor = connection.conn, connection.cursor


app = common.FastAPI()
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = exc.errors()
    modified_details = []
    for error in details:
        modified_details.append(
            {
                "location": error["loc"],
                "message": error["msg"],
            }
        )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": modified_details}),
    )


@app.get("/")
async def main_page():
    return {"message": "Hello World", "status_code": 200, "message": "OK"}

#cats

@app.get("/cat-facts/")
async def get_axoloti_onfo(token: str = common.Depends(oauth2_scheme)):
    data_facts = []
    common.decode_token(token)

    response = common.requests.get("https://cat-fact.herokuapp.com/facts")

    soup = common.BeautifulSoup(response.text, 'html.parser')

    text_content = soup.get_text()
    data = common.json.loads(text_content)
    for i in data:
        data_facts.append({"fact": i["text"]})

    data_facts.append({"status code": response.status_code})

    return data_facts

@app.get("/dubbings-languages/{language_id}")
async def get_dubbing_by_language_id(language_id: int, token: str = common.Query(...)):

    if common.decode_token(token) == "token is invalid":
        raise common.HTTPException(status_code=401, detail="token is invalid")

    try:
        query = """EXECUTE SelectDubbingByLanguageId @language_id = ?;"""
        cursor.execute(query, language_id)

    except common.pyodbc.IntegrityError as e:
        print(e)

    rows = cursor.fetchall()

    return len(rows)

@app.get("/registration-info")
async def get_registration_info(token: str = common.Query(...)):

    if common.decode_token(token) == "token is invalid":
        raise common.HTTPException(status_code=401, detail="token is invalid")

    try:

        query = """EXECUTE SelectRegistrationInfo;"""
        cursor.execute(query)

    except common.pyodbc.IntegrityError as e:
        print(e)

    rows = cursor.fetchall()
    result_list = []

    for row in rows:
        user_dict = {}
        for idx, column in enumerate(cursor.description):
            user_dict[column[0]] = str(row[idx])
        result_list.append(user_dict)

    return result_list

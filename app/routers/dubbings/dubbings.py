from app.common import (
    APIRouter,
    OAuth2PasswordBearer,
    Correct_Data,
    Header,
    Depends,
    status,
    BaseModels,
    decode_token
)
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

attributes_router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

correct_data = Correct_Data()

dubbings_router = APIRouter()


@dubbings_router.get("/dubbings")
async def get_dubbings(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
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

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept), "dubbing")


@dubbings_router.get("/dubbings/{dubbing_id}")
async def get_dubbings_by_id(dubbing_id: int, accept: str = Header(default="application/json"),
                             token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
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

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept), "dubbing")


@dubbings_router.post("/dubbings", status_code=status.HTTP_201_CREATED)
async def post_dubbings(dubbing_info: BaseModels.DubbingInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    if (dubbing_info.film_id is None and dubbing_info.episode_id is None) or (
            dubbing_info.film_id is not None and dubbing_info.episode_id is not None):
        raise HTTPException(status_code=400, detail="Wrong input")

    try:
        query = """EXECUTE InsertDubbing @film_id = ?, @episode_id = ?, @language_id = ?, @dubbing_company = ?;"""
        cursor.execute(query, dubbing_info.film_id, dubbing_info.episode_id, dubbing_info.language_id,
                       dubbing_info.dubbing_company)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Wrong input")

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return "Dubbing added successfully."


@dubbings_router.put("/dubbings/{dubbing_id}", status_code=status.HTTP_200_OK)
async def put_dubbings(dubbing_id: int, dubbing_info: BaseModels.DubbingInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE UpdateDubbing @dubbing_id = ?, @film_id = ?, @episode_id = ?, @language_id = ?, @dubbing_company = ?;"""
        cursor.execute(query, dubbing_id, dubbing_info.film_id, dubbing_info.episode_id, dubbing_info.language_id,
                       dubbing_info.dubbing_company)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    return f"Dubbing with id = {dubbing_id} edited successfully."


@dubbings_router.delete("/dubbings/{dubbing_id}")
async def delete_dubbings(dubbing_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE DeleteDubbing @dubbing_id = ?;"""
        cursor.execute(query, dubbing_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Dubbing with id = {dubbing_id} deleted successfully."
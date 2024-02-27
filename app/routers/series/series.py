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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

correct_data = Correct_Data()

series_router = APIRouter()

@series_router.get("/series")
async def get_series(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
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

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series")

@series_router.get("/series/{series_id}")
async def get_series_by_id(series_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
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

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series")

@series_router.post("/series", status_code=status.HTTP_201_CREATED)
async def post_series(series_info: BaseModels.SeriesInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE InsertSeries @title = ?, @episodeAmount = ?;"""
        cursor.execute(query, series_info.title, series_info.episode_amount)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Wrong input")

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return "Series added successfully."

@series_router.put("/series/{series_id}")
async def put_series(series_id: int, series_info: BaseModels.SeriesInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE UpdateSeries @series_id = ?, @title = ?, @episodeAmount = ?;"""
        cursor.execute(query, series_id, series_info.title, series_info.episode_amount)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    return f"Series with id = {series_id} edited successfully."

@series_router.delete("/series/{series_id}")
async def delete_series(series_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE DeleteSeries @series_id = ?;"""
        cursor.execute(query, series_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Series with id = {series_id} deleted successfully."
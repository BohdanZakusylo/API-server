import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor
oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

series_router = common.APIRouter()

@series_router.get("/series")
async def get_series(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

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

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series")

@series_router.get("/series/{series_id}")
async def get_series_by_id(series_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

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

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series")

@series_router.post("/series", status_code=common.status.HTTP_201_CREATED)
async def post_series(series_info: common.BaseModels.SeriesInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE InsertSeries @title = ?, @episodeAmount = ?;"""
        cursor.execute(query, series_info.title, series_info.episode_amount)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Series;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectSeriesById @series_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('SERVER')}:8000/series/{id}", "data": result_list}

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, "application/json" , "series")

@series_router.put("/series/{series_id}")
async def put_series(series_id: int, series_info: common.BaseModels.SeriesInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE UpdateSeries @series_id = ?, @title = ?, @episodeAmount = ?;"""
        cursor.execute(query, series_id, series_info.title, series_info.episode_amount)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=422, detail="Unprocessable Entity")

    return f"Series with id = {series_id} edited successfully."

@series_router.delete("/series/{series_id}")
async def delete_series(series_id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE DeleteSeries @series_id = ?;"""
        cursor.execute(query, series_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=400, detail="Wrong input")

    return f"Series with id = {series_id} deleted successfully."
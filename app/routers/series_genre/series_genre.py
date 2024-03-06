import app.common as common 
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

series_genre_router = common.APIRouter()

@series_genre_router.get("/series-genre")
async def get_series_genre(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectSeriesGenre];")
        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")


@series_genre_router.get("/series-genre/{series_id}")
async def get_series_genre_by_series_id(series_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectSeriesGenreBySeriesId] @series_id = {series_id};")
        rows = cursor.fetchall()
        result_list = []

        if not rows:
            raise common.HTTPException(status_code=404, detail="Series not found")

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")


@series_genre_router.get("/genre-series/{attribute_id}")
async def get_series_genre_by_attribute_id(attribute_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectSeriesGenreByAttributeId] @attribute_id = {attribute_id};")
        rows = cursor.fetchall()
        result_list = []

        if not rows:
            raise common.HTTPException(status_code=404, detail="Genre not found")

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")


@series_genre_router.post("/series-genre", status_code=common.status.HTTP_201_CREATED)
async def insert_series_genre(series_genre_info: common.BaseModels.SeriesGenerInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertSeriesGenre] @series_id = ?, @attribute_id = ?;"
        cursor.execute(query, series_genre_info.series_id, series_genre_info.attribute_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Invalid input. Input should be integer.")
    
    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Series genre inserted"}


@series_genre_router.put("/series-genre/{series_id}-{attribute_id}", status_code=common.status.HTTP_200_OK)
async def update_series_genre(series_id: int, attribute_id: int, series_genre_info: common.BaseModels.SeriesGenerInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [UpdateSeriesGenre] @series_id = ?, @attribute_id = ?, @new_series_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, series_id, attribute_id, series_genre_info.new_series_id, series_genre_info.new_attribute_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Series genre updated"}


@series_genre_router.delete("/series-genre/{series_id}-{attribute_id}")
async def delete_series_genre(series_id: int, attribute_id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteSeriesGenre] @series_id = ?, @attribute_id = ?;"
        cursor.execute(query, series_id, attribute_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Series genre naming is incorrect")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Series genre deleted"}
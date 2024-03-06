import app.common as common 
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

films_router = common.APIRouter()


@films_router.get("/film")
async def get_film(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectFilm];")
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
        if error_code == '42000' and ('The SELECT permission was denied on the object' in error_message or 'Invalid object name' in error_message):
            raise common.HTTPException(status_code=403, detail="Permission denied")
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film")


@films_router.get("/film/{id}")
async def get_film_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
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

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film")

@films_router.post("/film", status_code=common.status.HTTP_201_CREATED)
async def insert_film(film_info: common.BaseModels.FilmInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertFilm] @title = ?, @duration = ?;"
        cursor.execute(query, film_info.title, film_info.duration)
        conn.commit()
    
    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Film data is incorrect")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")
    
    return {"message": "Film inserted"}

@films_router.put("/film/{id}", status_code=common.status.HTTP_200_OK)
async def update_film(id: int, film_info: common.BaseModels.FilmInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try: 
        query = f"EXEC [UpdateFilm] @film_id = ?, @title = ?, @duration = ?;"
        cursor.execute(query, id, film_info.title, film_info.duration)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Film updated"}


@films_router.delete("/film/{id}")
async def delete_film(id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteFilm] @film_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Film data is incorrect")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Film deleted"}
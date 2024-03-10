import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

film_genre_router = common.APIRouter()

@film_genre_router.get("/film-genre")
async def get_film_genre(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectFilmGenre];")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept), "film-genre")


@film_genre_router.get("/film-genre/{film_id}")
async def get_film_genre_by_film_id(film_id: int, accept: str = common.Header(default="application/json"),
                                    token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectFilmGenreByFilmId] @film_id = {film_id};")
        rows = cursor.fetchall()
        result_list = []

        if not rows:
            raise common.HTTPException(status_code=404, detail="Film not found")

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept), "film-genre")


@film_genre_router.get("/genre-film/{attribute_id}")
async def get_film_genre_by_attribute_id(attribute_id: int, accept: str = common.Header(default="application/json"),
                                         token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectFilmGenreByAttributeId] @attribute_id = {attribute_id};")
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

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept), "film-genre")


@film_genre_router.post("/film-genre", status_code=common.status.HTTP_201_CREATED)
async def insert_film_genre(film_genre_info: common.BaseModels.FilmGenreInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertFilmGenre] @film_id = ?, @attribute_id = ?;"
        cursor.execute(query, film_genre_info.film_id, film_genre_info.attribute_id)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Film_Genre;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectFilmGenreByFilmId @film_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('API_ADDRESS')}:8000/film-genre/{id}", "data": result_list}

    except common.pyodbc.IntegrityError as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return correct_data.return_correct_format(response, "application/json" , "film-genre")


@film_genre_router.put("/film-genre/{film_id}-{attribute_id}", status_code=common.status.HTTP_200_OK)
async def update_preferred_attributes(film_id: int, attribute_id: int, film_genre_info: common.BaseModels.FilmGenreInfo,
                                      token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [UpdateFilmGenre] @film_id = ?, @attribute_id = ?, @new_film_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, film_id, attribute_id, film_genre_info.new_film_id, film_genre_info.new_attribute_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Film genre updated"}


@film_genre_router.delete("/film-genre/{film_id}-{attribute_id}")
async def delete_preferred_attribute(film_id: int, attribute_id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteFilmGenre] @film_id = ?, @attribute_id = ?;"
        cursor.execute(query, film_id, attribute_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Preferred attributes naming is incorrect")
    
    return {"message": "Film genre deleted"}
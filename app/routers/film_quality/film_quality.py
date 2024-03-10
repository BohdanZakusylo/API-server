import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

film_quality_router = common.APIRouter()


# @app.get("/profile-film-overview/{view_id}/{profile_id}")
# def get_view_profile_film_overview(view_id: int, profile_id: str, accept: str = common.Header(default="application/json"), film_id: int = common.Query(None), episode_id: int = common.Query(None), token: str = common.Depends(oauth2_scheme)):
#     id_to_paste = None

#     common.decode_token(token)

#     params_dict = {'film_id': film_id, 'episode_id': episode_id}

#     for name, value in params_dict.items():
#         if value is not None:
#             id_to_paste = value
#             variable_name = name
#             break

#     try:
#         cursor.execute(f"EXEC [SelectViewProfileFilmOverview] @view_id = {view_id}, @profile_id = {profile_id}, @variable_name = {variable_name}, @id_to_paste = {id_to_paste};")
#         rows = cursor.fetchall()
#         result_list = []

#         for row in rows:
#             user_dict = {}
#             for idx, column in enumerate(cursor.description):
#                 if column[0] == "date":
#                     user_dict[column[0]] = str(row[idx])
#                 else:
#                     user_dict[column[0]] = row[idx]
#             result_list.append(user_dict)
#         response = {"status": "200 OK", "data": result_list}

#     except pyodbc.ProgrammingError as programming_error:
#         error_code, error_message = programming_error.args
#         if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
#             raise HTTPException(status_code=403, detail="Permission denied")

#     return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile-film-overview-view")

@film_quality_router.get("/profile-film-overview")
def get_view_profile_film_overview_all(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectFilmQuality];")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "film-quality")


@film_quality_router.get("/film-quality/{film_id}")
async def get_film_quality_by_film_id(film_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectFilmQualityByFilmId] @film_id = {film_id};")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")

@film_quality_router.get("/quality-film/{quality_id}")
async def get_film_quality_by_quality_id(quality_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
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

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile-film-overview-view")


@film_quality_router.get("/quality-film/{quality_id}")
async def get_film_quality_by_quality_id(quality_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectFilmQualityByQualityId] @quality_id = {quality_id};")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "series-genre")

@film_quality_router.post("/film-quality", status_code=common.status.HTTP_201_CREATED)
async def insert_film_quality(film_quality_info: common.BaseModels.FilmQualityInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertFilmQuality] @film_id = ?, @quality_id = ?;"
        cursor.execute(query, film_quality_info.film_id, film_quality_info.quality_id)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Film_Quality;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectFilmQualityByFilmId @film_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('API_ADDRESS')}:8000/film-quality/{id}", "data": result_list}

    except common.pyodbc.IntegrityError as e:
        raise common.HTTPException(status_code=403, detail="Permission Denied")

    return correct_data.return_correct_format(response, "application/json", "film-quality")


@film_quality_router.put("/film-quality/{film_id}-{quality_id}", status_code=common.status.HTTP_200_OK)
async def update_film_quality(film_id: int, quality_id: int, film_quality_info: common.BaseModels.FilmQualityInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [UpdateFilmQuality] @film_id = ?, @quality_id = ?, @new_film_id = ?, @new_quality_id = ?;"
        cursor.execute(query, film_id, quality_id, film_quality_info.new_film_id, film_quality_info.new_quality_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return {"message:" "Film quality updated"}


@film_quality_router.delete("/film-quality/{film_id}-{quality_id}")
async def delete_film_quality(film_id: int, quality_id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteFilmQuality] @film_id = ?, @quality_id = ?;"
        cursor.execute(query, film_id, quality_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Film quality naming is incorrect")


    return {"message": "Film quality deleted"}
import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

subtitles_router = common.APIRouter()

@subtitles_router.get("/subtitle")
async def get_subtitle(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectSubtitle];")
        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                    user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.ProgrammingError:
        raise common.HTTPException(status_code=403, detail="Permission denied")
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subtitle")

@subtitles_router.get("/subtitle/{id}")
async def get_subtitle_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectSubtitleById] @subtitle_id = {id};")
        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                    user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.ProgrammingError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subtitle")

@subtitles_router.post("/subtitle", status_code=common.status.HTTP_201_CREATED)
async def insert_subtitle(subtitle_info: common.BaseModels.SubtitleInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertSubtitle] @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, subtitle_info.film_id, subtitle_info.episode_id, subtitle_info.language_id)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Subtitle;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectSubtitleById @subtitle_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('SERVER')}:8000/subtitle/{id}", "data": result_list}

    except common.pyodbc.IntegrityError as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return correct_data.return_correct_format(response, "application/json" , "subtitle")

@subtitles_router.put("/subtitle/{id}", status_code=common.status.HTTP_200_OK)
async def update_subtitle(id: int, subtitle_info: common.BaseModels.SubtitleInfo, token: str =common. Depends(oauth2_scheme)):
    common.decode_token(token)

    try: 
        query = f"EXEC [UpdateSubtitle] @subtitle_id = ?, @film_id = ?, @episode_id = ?, @language_id = ?;"
        cursor.execute(query, id, subtitle_info.film_id, subtitle_info.episode_id, subtitle_info.language_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Subtitle updated"}


@subtitles_router.delete("/subtitle/{id}")
async def delete_subtitle(id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteSubtitle] @subtitle_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Subtitle data is incorrect")

    except common.pyodbc.ProgrammingError as programming_error:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Subtitle deleted"}

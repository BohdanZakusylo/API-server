import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

attributes_router = common.APIRouter()

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

episodes_router = common.APIRouter()


@episodes_router.get("/episode")
async def get_episode(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectEpisode];")
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
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "episode")

@episodes_router.get("/episode/{id}")
async def get_episode_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectEpisodeById] @episode_id = {id};")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "episode")

@episodes_router.post("/episode", status_code=common.status.HTTP_201_CREATED)
async def insert_episode(episode_info: common.BaseModels.EpisodeInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertEpisode] @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, episode_info.series_id, episode_info.title, episode_info.duration, episode_info.episode_number)
        conn.commit()
    
    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Episode data is incorrect")
    
    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")
        
    return {"message": "Episode inserted"}


@episodes_router.put("/episode/{id}", status_code=common.status.HTTP_200_OK)
async def update_episode(id: int, episode_info: common.BaseModels.EpisodeInfo, token: str =common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try: 
        query = f"EXEC [UpdateEpisode] @episode_id = ?, @series_id = ?, @title = ?, @duration = ?, @episode_number = ?;"
        cursor.execute(query, id, episode_info.series_id, episode_info.title, episode_info.duration, episode_info.episode_number)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Episode updated"}

@episodes_router.delete("/episode/{id}")
async def delete_episode(id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteEpisode] @episode_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Episode data is incorrect")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Episode deleted"}
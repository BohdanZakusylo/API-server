import app.common as common 
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

quality_router = common.APIRouter()

@quality_router.get("/quality")
async def get_quality(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectQuality];")
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
        
    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "quality")

@quality_router.get("/quality/{id}")
async def get_quality_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectQualityById] @quality_id = {id};")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "quality")

@quality_router.post("/quality", status_code=common.status.HTTP_201_CREATED)
async def insert_quality(quality_info: common.BaseModels.QualityInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertQuality] @quality_type = ?;"
        cursor.execute(query, quality_info.quality_type)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Quality;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectQualityById @quality_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('SERVER')}:8000/quality/{id}", "data": result_list}

    except common.pyodbc.IntegrityError as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return correct_data.return_correct_format(response, "application/json" , "quality")


@quality_router.put("/quality/{id}", status_code=common.status.HTTP_200_OK)
async def update_quality(id: int, quality_info: common.BaseModels.QualityInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try: 
        query = f"EXEC [UpdateQuality] @quality_id = ?, @quality_type = ?;"
        cursor.execute(query, id, quality_info.quality_type)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Quality updated"}


@quality_router.delete("/quality/{id}")
async def delete_quality(id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteQuality] @quality_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Quality data is incorrect")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Quality deleted"}
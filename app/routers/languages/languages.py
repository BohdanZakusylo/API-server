import app.common as common 
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

languages_router = common.APIRouter()


@languages_router.get("/language")
async def get_languages(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectLanguage];")
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


    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "languages")


@languages_router.get("/language/{id}")
async def get_languages_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectLanguageById] @language_id = {id};")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "languages")

@languages_router.post("/language", status_code=common.status.HTTP_201_CREATED)
async def insert_languages(language_info: common.BaseModels.LanguageInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)
        
    try:
        query = f"EXEC [InsertLanguage] @language_name = ?;"
        cursor.execute(query, language_info.language_name)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Language;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectLanguageById @language_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('SERVER')}:8000/language/{id}", "data": result_list}

    except common.pyodbc.IntegrityError as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return correct_data.return_correct_format(response, "application/json" , "language")

@languages_router.put("/language/{id}", status_code=common.status.HTTP_200_OK)
async def update_languages(id: int, language_info: common.BaseModels.LanguageInfo, token: str = common.Depends(oauth2_scheme)):

    common.decode_token(token)

    try: 
        query = f"EXEC [UpdateLanguage] @language_id = ?, @language_name = ?;"
        cursor.execute(query, id, language_info.language_name)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Language updated"}

@languages_router.delete("/language/{id}")
async def delete_languages(id: int, token: str = common.Depends(oauth2_scheme)):

    common.decode_token(token)

    try:
        query = f"EXEC [DeleteLanguage] @language_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Language naming is incorrect")

    except common.pyodbc.ProgrammingError as programming_error:
        error_code, error_message = programming_error.args
        if error_code == '42000' and 'The EXECUTE permission was denied on the object' in error_message:
            raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Language deleted"}
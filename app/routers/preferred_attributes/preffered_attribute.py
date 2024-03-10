import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

preferred_attributes_router = common.APIRouter()

@preferred_attributes_router.get("/preferred-attribute")
async def get_preferred_attribute(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectPreferredAttribute];")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "preferred-attribute")

@preferred_attributes_router.get("/preferred-attribute/{profile_id}")
async def get_preferred_attribute_by_profile_id(profile_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectPreferredAttributeByProfileId] @profile_id = {profile_id};")
        rows = cursor.fetchall()
        result_list = []

        if not rows:
            raise common.HTTPException(status_code=404, detail="Profile not found")

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "preferred-attribute")

@preferred_attributes_router.post("/preferred-attribute", status_code=common.status.HTTP_201_CREATED)
async def insert_preferred_attribute(preferred_attribute_info: common.BaseModels.PreferredAttributeInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [InsertPreferredAttribute] @profile_id = ?, @attribute_id = ?;"
        cursor.execute(query, preferred_attribute_info.profile_id, preferred_attribute_info.attribute_id)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Preferred_Attribute;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectPreferredAttributeByProfileId @profile_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('API_ADDRESS')}:8000/preferred-attribute/{id}", "data": result_list}

    except common.pyodbc.IntegrityError as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return correct_data.return_correct_format(response, "application/json" , "preferred-attribute")

@preferred_attributes_router.put("/preferred-attribute/{profile_id}-{attribute_id}", status_code=common.status.HTTP_200_OK)
async def update_preferred_attributes(profile_id: int, attribute_id: int, preferred_attribute_info: common.BaseModels.PreferredAttributeInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [UpdatePreferredAttribute] @profile_id = ?, @attribute_id = ?, @new_profile_id = ?, @new_attribute_id = ?;"
        cursor.execute(query, profile_id, attribute_id, preferred_attribute_info.new_profile_id, preferred_attribute_info.new_attribute_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Preferred attribute updated"}

@preferred_attributes_router.delete("/preferred-attribute/{profile_id}-{attribute_id}")
async def delete_preferred_attribute(profile_id: int, attribute_id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeletePreferredAttribute] @profile_id = ?, @attribute_id = ?;"
        cursor.execute(query, profile_id, attribute_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Preferred attributes naming is incorrect")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return {"message": "Preferred attribute deleted"}
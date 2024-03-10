import app.common as common
import  app.connection as connection

conn, cursor = connection.conn, connection.cursor

attributes_router = common.APIRouter()

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

@attributes_router.get("/attributes")
async def get_attributes(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectAtribute];")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "attributes")

@attributes_router.get("/attributes/{id}")
async def get_attributes_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectAttributeById] @attribute_id = {id};")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "attributes")

@attributes_router.post("/attributes", status_code=common.status.HTTP_201_CREATED)
async def insert_atributes(attribute_data: common.BaseModels.AttributesInfo, token: str = common.Depends(oauth2_scheme)):

    common.decode_token(token)
    
    try:
        query = f"EXEC [InsertAttribute] @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, attribute_data.attribute_type, attribute_data.attribute_description)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Attribute;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectAttributeById @attribute_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('SERVER')}:8000/attribute/{id}", "data": result_list}

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, "application/json", "attribute")

@attributes_router.put("/attributes/{id}", status_code=common.status.HTTP_200_OK)
async def update_attributes(id: int, attribute_info: common.BaseModels.AttributesInfo, token: str = common.Depends(oauth2_scheme)):

    common.decode_token(token)

    try: 
        query = f"EXEC [UpdateAttribute] @attribute_id = ?, @attribute_type = ?, @attribute_description = ?;"
        cursor.execute(query, id, attribute_info.attribute_type, attribute_info.attribute_description)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Atribute updated"}

@attributes_router.delete("/atributes/{id}")
async def delete_attributes(id: int, token: str =common.Depends(oauth2_scheme)):

    common.decode_token(token)

    try:
        query = f"EXEC [DeleteAttribute] @attribute_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Attributes naming is incorrect")

    return {"message": "Atribute deleted"}
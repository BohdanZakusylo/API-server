import app.common as common 
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

profiles_router = common.APIRouter()


@profiles_router.get("/profile")
async def get_profile(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectProfile];")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile")


@profiles_router.get("/profile/{id}")
async def get_profile_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXEC [SelectProfileById] @profile_id = {id};")
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

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "profile")


@profiles_router.post("/profile", status_code=common.status.HTTP_201_CREATED)
async def insert_profile(profile_info: common.BaseModels.ProfileInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)
    try:
        query = f"EXEC [InsertProfile] @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, profile_info.user_id, profile_info.age, profile_info.nick_name, profile_info.profile_picture)
        conn.commit()
        query = """EXEC [GetLastItemIdOfTable] Profile;"""
        cursor.execute(query)
        id = (cursor.fetchone())
        id = id[0]
        query = """EXECUTE SelectProfileById @profile_id = ?;"""
        cursor.execute(query, id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        
        response = {"Location": rf"http://{common.os.getenv('API_ADDRESS')}:8000/profile/{id}", "data": result_list}

    except common.pyodbc.IntegrityError as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return correct_data.return_correct_format(response, "application/json" , "profile")


@profiles_router.put("/profile/{id}", status_code=common.status.HTTP_200_OK)
async def update_profile(id: int, profile_info: common.BaseModels.ProfileInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try: 
        query = f"EXEC [UpdateProfile] @profile_id = ?, @user_id = ?, @age = ?, @nick_name = ?, @profile_picture = ?;"
        cursor.execute(query, id, profile_info.user_id, profile_info.age, profile_info.nick_name, profile_info.profile_picture)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    return {"message": "Profile updated"}

@profiles_router.delete("/profile/{id}")
async def delete_profile(id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = f"EXEC [DeleteProfile] @profile_id = ?;"
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Profile data is incorrect")

    return {"message": "Profile deleted"}
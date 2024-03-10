import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

users_router = common.APIRouter()


@users_router.get("/users")
async def get_users(accept: str = common.Header(default="application/json"), token: str =  common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXECUTE SelectUser;")
        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                if "password" in column[0]:
                    pass
                else:
                    user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.ProgrammingError as programming_error:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user")

@users_router.get("/users/{id}")
async def get_users_by_id(id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        cursor.execute(f"EXECUTE SelectUserById @user_id = {id};")
        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                if 'password' in column[0]:
                    pass
                else:
                    user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "user")

@users_router.put("/users/{id}", status_code=common.status.HTTP_200_OK)
async def put_users(id: int, update_user_info: common.BaseModels.UpdateUserInfo, token: str = common.Depends(oauth2_scheme)):
    #TODO check if user wants to update itself
    common.decode_token(token)

    try:

        query = """EXECUTE UpdateUser @user_id = ?, @username = ?, @language_id = ?, @password = ?, @is_activated = ?, @is_blocked = ?, @email = ?;"""
        cursor.execute(query, id, update_user_info.username, update_user_info.language_id, update_user_info.password, update_user_info.is_activated, update_user_info.is_blocked, update_user_info.login_info.email)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=422, detail="Unprocessable Entity")

    cursor.execute(f"EXECUTE SelectUserById @user_id = {id};")

    id = cursor.fetchone()[0]

    return {
        "token": common.encode_token(id, update_user_info.username)
    }

@users_router.delete("/users/{id}")
async def delete_users(id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE DeleteUser @user_id = ?;"""
        cursor.execute(query, id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Email should be unique")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=404, detail="User not found")

    return f"User with id = {id} deleted successfully."
import app.common as common
import  app.connection as connection
from app.base_classes.base_classes import BaseModels

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

conn, cursor = connection.conn, connection.cursor

login_router = common.APIRouter()

correct_data = common.Correct_Data()

@login_router.post("/registration", status_code=common.status.HTTP_201_CREATED)
async def registration(registration_info: common.BaseModels.RegistrationIngfo):

    try:
        query = """EXECUTE [InsertUser] @email = ?, @password = ?, @username = ?, @age = ?;"""
        cursor.execute(query, registration_info.email, registration_info.password, registration_info.username, registration_info.age)
        conn.commit()
        
    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Username and email should be unique")

    except Exception:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=422, detail="Username and email should be unique")

    cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].email = '{registration_info.email}';")

    try:
        id = cursor.fetchone()[0]

    except TypeError:
        raise common.HTTPException(status_code=409, detail="User already exists")
    

    encoded_refresh_token = common.encode_refresh_token()
    print(encoded_refresh_token)

    try:
        query = """[UpdateRefreshToken] @user_id = ?, @refreshToken = ?;"""
        cursor.execute(query, id, encoded_refresh_token)
        conn.commit()
        
    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=500, detail="Try again later")    


    return {
        "token": common.encode_token(id, registration_info.username), 
        "refresh_token": encoded_refresh_token
    }

@login_router.get("/login")
async def login(login_info: common.BaseModels.LoginInfo):
    try:
        query = """EXEC [CheckUserPassword] @email = ?, @password = ?;"""
        cursor.execute(query, login_info.email, login_info.password)
        result = cursor.fetchone()[0]
    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=404, detail="User not found")

    if not result:
        raise common.HTTPException(status_code=401, detail="Wrong email or password")
    else:
        query = """EXEC [GetCredential] @email = ?"""
        cursor.execute(query, login_info.email)
        rows = cursor.fetchall()
        result_list = []
        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"data": result_list, "token": common.encode_token(int(result_list[0].get('user_id', 0)), login_info.email)}
        return response

@login_router.get("/new-token")
def get_token_by_refresh_token(refresh_token: common.BaseModels.RefreshtokenInfo):
    user_id, name = common.decode_refresh_token(refresh_token.refresh_token)

    try:
        cursor.execute(f"SELECT [user].user_id FROM [user] WHERE [user].user_id = {user_id};")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.fetchone() is None:
        raise common.HTTPException(status_code=404, detail="User not found")

    return {
        "token": common.encode_token(user_id, name),
    }
from app.common import (
    APIRouter,
    OAuth2PasswordBearer,
    Correct_Data,
    Header,
    Depends,
    status,
    BaseModels,
    decode_token, 
    pyodbc, 
    HTTPException
)
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

correct_data = Correct_Data()

subscriptions_router = APIRouter()

@subscriptions_router.get("/subscriptions")
async def get_subscriptions(accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE SelectSubscription;"""
        cursor.execute(query)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subscription")

@subscriptions_router.get("/subscriptions/{subscription_id}")
async def get_subscriptions_by_id(subscription_id: int, accept: str = Header(default="application/json"), token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE SelectSubscriptionById @subscription_id = ?;"""
        cursor.execute(query, subscription_id)

        rows = cursor.fetchall()
        result_list = []

        for row in rows:
            user_dict = {}
            for idx, column in enumerate(cursor.description):
                user_dict[column[0]] = str(row[idx])
            result_list.append(user_dict)
        response = {"status": "200 OK", "data": result_list}

        return correct_data.return_correct_format(response, correct_data.validate_data_type(accept) , "subscription")

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

@subscriptions_router.post("/subscriptions", status_code=status.HTTP_201_CREATED)
async def post_subscriptions(subscription_info: BaseModels.SubscriptionInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE InsertSubscription @user_id = ?, @type = ?, @price = ?, @start_date = ?, @expiration_date = ?, @is_discount = ?;"""
        cursor.execute(query, subscription_info.user_id, subscription_info.type, subscription_info.price, subscription_info.start_date, subscription_info.expiration_date, subscription_info.is_discount)
        conn.commit()
    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Wrong input")

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return "Subscription added successfully."

@subscriptions_router.put("/subscriptions/{subscription_id}", status_code=status.HTTP_200_OK)
async def put_subscriptions(subscription_id: int, subscription_info: BaseModels.SubscriptionInfo, token: str = Depends(oauth2_scheme)):
    decode_token(token)
    try:
        query = """EXECUTE UpdateSubscription @subscription_id = ?, @user_id = ?, @type = ?, @price = ?, @start_date = ?, @expiration_date = ?, @is_discount = ?;"""
        cursor.execute(query, subscription_id, subscription_info.user_id, subscription_info.type, subscription_info.price, subscription_info.start_date, subscription_info.expiration_date, subscription_info.is_discount)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Something went wrong")

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=422, detail="Unprocessable Entity")

    return f"Subscription with id = {subscription_id} edited successfully."

@subscriptions_router.delete("/subscriptions/{subscription_id}")
async def delete_subscriptions(subscription_id: int, token: str = Depends(oauth2_scheme)):
    decode_token(token)

    try:
        query = """EXECUTE DeleteSubscription @subscription_id = ?;"""
        cursor.execute(query, subscription_id)
        conn.commit()

    except pyodbc.IntegrityError:
        raise HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise HTTPException(status_code=400, detail="Wrong input")

    return f"Subscription with id = {subscription_id} deleted successfully."

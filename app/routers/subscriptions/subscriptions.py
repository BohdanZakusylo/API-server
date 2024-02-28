import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()

subscriptions_router = common.APIRouter()

@subscriptions_router.get("/subscriptions")
async def get_subscriptions(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

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

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    return common.correct_data.return_correct_format(response, common.correct_data.validate_data_type(accept) , "subscription")

@subscriptions_router.get("/subscriptions/{subscription_id}")
async def get_subscriptions_by_id(subscription_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

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

        return common.correct_data.return_correct_format(response, common.correct_data.validate_data_type(accept) , "subscription")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

@subscriptions_router.post("/subscriptions", status_code=common.status.HTTP_201_CREATED)
async def post_subscriptions(subscription_info: common.BaseModels.SubscriptionInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE InsertSubscription @user_id = ?, @type = ?, @price = ?, @start_date = ?, @expiration_date = ?, @is_discount = ?;"""
        cursor.execute(query, subscription_info.user_id, subscription_info.type, subscription_info.price, subscription_info.start_date, subscription_info.expiration_date, subscription_info.is_discount)
        conn.commit()
    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Wrong input")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=400, detail="Wrong input")

    return "Subscription added successfully."

@subscriptions_router.put("/subscriptions/{subscription_id}", status_code=common.status.HTTP_200_OK)
async def put_subscriptions(subscription_id: int, subscription_info: common.BaseModels.SubscriptionInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)
    try:
        query = """EXECUTE UpdateSubscription @subscription_id = ?, @user_id = ?, @type = ?, @price = ?, @start_date = ?, @expiration_date = ?, @is_discount = ?;"""
        cursor.execute(query, subscription_id, subscription_info.user_id, subscription_info.type, subscription_info.price, subscription_info.start_date, subscription_info.expiration_date, subscription_info.is_discount)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=422, detail="Unprocessable Entity")

    return f"Subscription with id = {subscription_id} edited successfully."

@subscriptions_router.delete("/subscriptions/{subscription_id}")
async def delete_subscriptions(subscription_id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE DeleteSubscription @subscription_id = ?;"""
        cursor.execute(query, subscription_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=400, detail="Wrong input")

    return f"Subscription with id = {subscription_id} deleted successfully."

import app.common as common
import app.connection as connection

conn, cursor = connection.conn, connection.cursor

oauth2_scheme = common.OAuth2PasswordBearer(tokenUrl="token")

correct_data = common.Correct_Data()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

watchlists_router = common.APIRouter()

@watchlists_router.get("/watchlists")
async def get_watchlists(accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE SelectWatchlist_Item;"""
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

    return common.correct_data.return_correct_format(response, common.correct_data.validate_data_type(accept) , "watchlist_item")

@watchlists_router.get("/watchlists/{watchlist_item_id}")
async def get_watchlists_by_id(watchlist_item_id: int, accept: str = common.Header(default="application/json"), token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE SelectWatchlist_ItemById @watchlist_item_id = ?;"""
        cursor.execute(query, watchlist_item_id)

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

@watchlists_router.post("/watchlists", status_code=common.status.HTTP_201_CREATED)
async def post_watchlist_item(watchlist_item_info: common.BaseModels.WatchlistItemInfo, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    if (watchlist_item_info.film_id is None and watchlist_item_info.series_id is None) or (watchlist_item_info.film_id is not None and watchlist_item_info.series_id is not None):
        raise common.HTTPException(status_code=400, detail="Wrong input")

    try:
        query = """EXECUTE InsertWatchlist_Item @profile_id = ?, @series_id = ?, @film_id = ?, @is_finished = ?;"""
        cursor.execute(query, watchlist_item_info.profile_id, watchlist_item_info.series_id, watchlist_item_info.film_id, watchlist_item_info.is_finished)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Wrong input")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=400, detail="Wrong input")

    return "Watchlist item added successfully."

@watchlists_router.put("/watchlists/{watchlist_item_id}", status_code=common.status.HTTP_200_OK)
async def put_watchlist_item(watchlist_item_id: int, watchlist_item_info: common.BaseModels.WatchlistItemInfo, token: str = common.Depends(oauth2_scheme)):

    if (watchlist_item_info.film_id is None and watchlist_item_info.series_id is None) or (watchlist_item_info.film_id is not None and watchlist_item_info.series_id is not None):
        raise common.HTTPException(status_code=400, detail="Wrong input")

    common.decode_token(token)

    try:
        query = """EXECUTE UpdateWatchlist_Item @watchlist_item_id = ?, @profile_id = ?, @series_id = ?, @film_id = ?, @is_finished = ?;"""
        cursor.execute(query, watchlist_item_id, watchlist_item_info.profile_id, watchlist_item_info.series_id, watchlist_item_info.film_id, watchlist_item_info.is_finished)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=400, detail="Validation Error.")

    except Exception as e:
        raise common.HTTPException(status_code=500, detail="Something went wrong")

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=422, detail="Unprocessable Entity")

    return f"Watchlist item with id = {watchlist_item_id} edited successfully."

@watchlists_router.delete("/watchlists/{watchlist_item_id}")
async def delete_watchlist_item(watchlist_item_id: int, token: str = common.Depends(oauth2_scheme)):
    common.decode_token(token)

    try:
        query = """EXECUTE DeleteWatchlist_Item @watchlist_item_id = ?;"""
        cursor.execute(query, watchlist_item_id)
        conn.commit()

    except common.pyodbc.IntegrityError:
        raise common.HTTPException(status_code=403, detail="Permission denied")

    if cursor.rowcount <= 0:
        raise common.HTTPException(status_code=400, detail="Wrong input")

    return f"Watchlist item with id = {watchlist_item_id} deleted successfully."

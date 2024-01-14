import pytest
import json
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


# def test_registration(client):
#     new_unique_user = client.post(
#         "http://127.0.0.1:8000/registration",

#         json={
#             "email": "Not@gmail.com",
#             "password": "1f2d",
#             "username": "Why",
#             "age": 25
#         },
#     )

#     assert new_unique_user.status_code == 200
#     assert "token" in new_unique_user.json()

#     old_user = client.post(
#         "http://127.0.0.1:8000/registration",

#         json={
#             "email": "Ivanl@gmail.com",
#             "password": "1f2d",
#             "username": "Ivan",
#             "age": 25
#         }, 

#     )

#     assert old_user.status_code == 404


# def test_refresh_token(client):
#     bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjMwLCJ1c2VybmFtZSI6Ikkxbm4xMXZhbiIsImV4cGlyYXRpb25fdGltZSI6MTcwNTI2MDUyNC44ODI2MTV9.aiSXoVvmsEgpc9CEtZbf8LtQlj-BCSCufclhEfot2yAPlK_XXmHMhn7RZvVOqDuQ3rGCa0TOwLxFDmELB8eUOlCPp6dov38wiQrWsXtxmwpJU7Kt0-XS2-2QztBzZ3HP-JDm_RA3_ewmZHx83jLl69I3SztEbRgfFhukr0qJLW_Sg4IEcKHYEavMYHrD1M2imbhK8s7RNaFhyHXF_J5Bs3ltq4wQKMf8GoXUoUs-u0yEH6peASzAKpwGFWNCTsMluBPCxebn-FcVa_8_i8cEXZlimXJr964jl2WvxonUdvyBGKSaoWyU4snF_Y_LpR9ZPrgkguV2MqFItTFJ9Pr4Bg"

#     headers = {'Authorization': f"Bearer {bearer_token}"}

#     new_refresh_token = client.get(
#         "http://127.0.0.1:8000/refresh-token",
#         headers=headers
#     )

#     assert "refresh_token" in new_refresh_token.json()

# def test_new_token(client):
#     bearer_refresh_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjMwLCJ1c2VybmFtZSI6Ikkxbm4xMXZhbiIsInR5cGUiOiJyZWZyZXNoIiwiZXhwaXJhdGlvbl90aW1lIjoxNzM2NzkzMTg2LjU1NTI0Nn0.kmRPk3KD78f_Q4YZyKaobqPAMeaZzqmy20PH4BLmiFpqHUQLnFFWxjprUZaW0-z_KDNacS_e7owO65RW9Wbo0fL7qQ3_ZIko45BPFcHwMzJKVYgUaDXWoBohMuRwEqKtknHmEBGSurbeqRM6fXhtmCPHrX-3opnOQBD50VxiWnPJi9sd6sNMc4U68qCySFCiGoCholF8tHCaDW73x6hp5H8yVBv2rmfk20sDJ2nNQyHPbbRIE0KipmoBdbggzlH-d0jxU-zAAi1AGRDOKCyKs1yWnwqZQMyUm0wVCGlHJ0uA-ZAQiKOp1w8G8pnr5dmKwBcufGDeVZV1GrmqUQ7NEg"

#     headers = {'Authorization': f"Bearer {bearer_refresh_token}"}

#     new_token = client.get(
#         "http://127.0.0.1:8000/new-token",
#         headers=headers,
#     )

#     assert "token" in new_token.json()

def test_atributes_all_data_type(client):
    bearer_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MjMwLCJ1c2VybmFtZSI6Ikkxbm4xMXZhbiIsImV4cGlyYXRpb25fdGltZSI6MTcwNTI2MDUyNC44ODI2MTV9.aiSXoVvmsEgpc9CEtZbf8LtQlj-BCSCufclhEfot2yAPlK_XXmHMhn7RZvVOqDuQ3rGCa0TOwLxFDmELB8eUOlCPp6dov38wiQrWsXtxmwpJU7Kt0-XS2-2QztBzZ3HP-JDm_RA3_ewmZHx83jLl69I3SztEbRgfFhukr0qJLW_Sg4IEcKHYEavMYHrD1M2imbhK8s7RNaFhyHXF_J5Bs3ltq4wQKMf8GoXUoUs-u0yEH6peASzAKpwGFWNCTsMluBPCxebn-FcVa_8_i8cEXZlimXJr964jl2WvxonUdvyBGKSaoWyU4snF_Y_LpR9ZPrgkguV2MqFItTFJ9Pr4Bg"

    headers = {'Authorization': f"Bearer {bearer_token}"}

    attr = client.get(
        "http://127.0.0.1:8000/atributes/json",
        headers=headers
    )

    assert attr.status_code == 200

    attr = client.get(
        "http://127.0.0.1:8000/atributes/xml",
        headers=headers
    )

    assert attr.status_code == 200
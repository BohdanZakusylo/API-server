import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_registration(client):
    new_unique_user = client.post(
        "http://127.0.0.1:8000/registration",

        json={
            "email": "Not@gmail.com",
            "password": "1f2d",
            "username": "Why",
            "age": 25
        },
    )

    assert new_unique_user.status_code == 200
    assert "token" in new_unique_user.json()

    old_user = client.post(
        "http://127.0.0.1:8000/registration",

        json={
            "email": "Ivanl@gmail.com",
            "password": "1f2d",
            "username": "Ivan",
            "age": 25
        }, 

    )

    assert old_user.status_code == 404
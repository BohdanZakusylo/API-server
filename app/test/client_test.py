import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture()
def client():
    return TestClient(app)


def test_registration(client):
    response = client.post(
        "/registration",
        json={
            "email": "3d333dtffffffarnnfffo@gmail.com",
            "password": "1f2d",
            "username": "dffddvfffff3dff333dd",
            "age": 25
        },
    )

    assert response.status_code == 200
    assert "token" in response.json()
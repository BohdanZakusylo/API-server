from fastapi.testclient import TestClient
import app.main as main

client = TestClient(main.app)

oauth2_token = """eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NDE0LCJ1c2VybmFtZSI6Imlka2Rpa2RpIiwiZXhwaXJhdGlvbl90aW1lIjoxNzA5NzMwMzU3Ljg1OTczNX0.dT_4h0WPlrPmsEdFnNpl9jZBAlLoJ7AbDTea0fualpOo2Bf6fYQDOy0LUd2votyaB2FB59lwba_C18vz7vy5LdFgExJ_r_vX7kth5i5v0R3bsBrZg4-swwFHL1bXZVGmCBnfSjUpMzvqjCvpzPI__XoX2Jwmb7RXRZYeeOgHexILSEBKuEcVRjDF4C6vvK_CBRR_WAk3yx2CFp7weVUVyducPwY1GAQAJ5blPbpq9muDJcfygT4rwXX7n48XvmiAJMig4v38fvFnySTDd6seSDvqIdn9ts9PjMAY9ay67U7f-uW52P499ayJ3VikqYlRtBA9-ExQswCrDpYKI0B58w"""

# Test for GET /attributes
def test_get_attributes():
    response = client.get("/attributes", headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "data" in response.json()

# Test for GET /attributes/{id}
def test_get_attributes_by_id():
    response = client.get("/attributes/1", headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "data" in response.json()

# Test for POST /attributes
def test_insert_attributes():
    data = {
        "attribute_type": "TestType",
        "attribute_description": "TestDescription"
    }
    response = client.post("/attributes", json=data, headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 201
    assert response.headers["content-type"] == "application/json"
    assert "message" in response.json()

# Test for PUT /attributes/{id}
def test_update_attributes():
    data = {
        "attribute_type": "UpdatedTestType",
        "attribute_description": "UpdatedTestDescription"
    }
    response = client.put("/attributes/1", json=data, headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "message" in response.json()

# Test for DELETE /attributes/{id}
def test_delete_attributes():
    response = client.delete("/attributes/1", headers={"Authorization": f"Bearer {oauth2_token}"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "message" in response.json()

#Tests for Dubbings
def test_get_dubbings():
    response = client.get("/dubbings")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_dubbings_by_id():
    dubbing_id = 1
    response = client.get(f"/dubbings/{dubbing_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) == 1

def test_post_dubbings():
    dubbing_info = {
        "film_id": 1,
        "episode_id": 1,
        "language_id": 1,
        "dubbing_company": "Test Dubbing Company"
    }
    response = client.post("/dubbings", json=dubbing_info)
    assert response.status_code == 201
    assert response.text == "Dubbing added successfully."

def test_put_dubbings():
    dubbing_id = 1
    dubbing_info = {
        "film_id": 2,
        "episode_id": 2,
        "language_id": 2,
        "dubbing_company": "Updated Dubbing Company"
    }
    response = client.put(f"/dubbings/{dubbing_id}", json=dubbing_info)
    assert response.status_code == 200
    assert f"Dubbing with id = {dubbing_id} edited successfully." in response.text

def test_delete_dubbings():
    dubbing_id = 1
    response = client.delete(f"/dubbings/{dubbing_id}")
    assert response.status_code == 200
    assert f"Dubbing with id = {dubbing_id} deleted successfully." in response.text

#Tests for episodes
def test_get_episode():
    response = client.get("/episode")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_episode_by_id():
    episode_id = 1  # Assuming 1 is a valid episode ID
    response = client.get(f"/episode/{episode_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) == 1  # Assuming we get one episode back

def test_insert_episode():
    episode_info = {
        "series_id": 1,
        "title": "Test Episode",
        "duration": "00:30:00",
        "episode_number": 1
    }
    response = client.post("/episode", json=episode_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Episode inserted"

def test_update_episode():
    episode_id = 1  # Assuming 1 is a valid episode ID
    episode_info = {
        "series_id": 1,
        "title": "Updated Episode",
        "duration": "00:45:00",
        "episode_number": 2
    }
    response = client.put(f"/episode/{episode_id}", json=episode_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Episode updated"

def test_delete_episode():
    episode_id = 1  # Assuming 1 is a valid episode ID
    response = client.delete(f"/episode/{episode_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Episode deleted"

#Tests for Film_genre
def test_get_film_genre():
    response = client.get("/film-genre")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_film_genre_by_film_id():
    film_id = 1
    response = client.get(f"/film-genre/{film_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_film_genre_by_attribute_id():
    attribute_id = 1
    response = client.get(f"/genre-film/{attribute_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_insert_film_genre():
    film_genre_info = {
        "film_id": 1,
        "attribute_id": 1
    }
    response = client.post("/film-genre", json=film_genre_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Film genre inserted"

def test_update_preferred_attributes():
    film_id = 1
    attribute_id = 1
    film_genre_info = {
        "new_film_id": 2,
        "new_attribute_id": 2
    }
    response = client.put(f"/film-genre/{film_id}-{attribute_id}", json=film_genre_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Film genre updated"

def test_delete_preferred_attribute():
    film_id = 1
    attribute_id = 1
    response = client.delete(f"/film-genre/{film_id}-{attribute_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Film genre deleted"

#Tests for Film_Quality
def test_get_film_quality():
    response = client.get("/film-quality")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_film_quality_by_film_id():
    film_id = 1  # Assuming 1 is a valid film ID
    response = client.get(f"/film-quality/{film_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_film_quality_by_quality_id():
    quality_id = 1  # Assuming 1 is a valid quality ID
    response = client.get(f"/quality-film/{quality_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_insert_film_quality():
    film_quality_info = {
        "film_id": 1,
        "quality_id": 1
    }
    response = client.post("/film-quality", json=film_quality_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Film quality inserted"

def test_update_film_quality():
    film_id = 1  # Assuming 1 is a valid film ID
    quality_id = 1  # Assuming 1 is a valid quality ID
    film_quality_info = {
        "new_film_id": 2,
        "new_quality_id": 2
    }
    response = client.put(f"/film-quality/{film_id}-{quality_id}", json=film_quality_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Film quality updated"

def test_delete_film_quality():
    film_id = 1  # Assuming 1 is a valid film ID
    quality_id = 1  # Assuming 1 is a valid quality ID
    response = client.delete(f"/film-quality/{film_id}-{quality_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Film quality deleted"

#Tests for Films
def test_get_film():
    response = client.get("/film")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_film_by_id():
    film_id = 1  # Replace with a valid film ID
    response = client.get(f"/film/{film_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_insert_film():
    film_info = {
        "title": "Test Film",
        "duration": 120
    }
    response = client.post("/film", json=film_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Film inserted"

def test_update_film():
    film_id = 1  # Replace with a valid film ID
    film_info = {
        "title": "Updated Film Title",
        "duration": 150
    }
    response = client.put(f"/film/{film_id}", json=film_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Film updated"

def test_delete_film():
    film_id = 1  # Replace with a valid film ID
    response = client.delete(f"/film/{film_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Film deleted"

#Tests for languages
def test_get_languages():
    response = client.get("/language")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_languages_by_id():
    language_id = 1  # Replace with a valid language ID
    response = client.get(f"/language/{language_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_insert_language():
    language_info = {
        "language_name": "Test Language"
    }
    response = client.post("/language", json=language_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Language inserted"

def test_update_language():
    language_id = 1  # Replace with a valid language ID
    language_info = {
        "language_name": "Updated Language Name"
    }
    response = client.put(f"/language/{language_id}", json=language_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Language updated"

def test_delete_language():
    language_id = 1  # Replace with a valid language ID
    response = client.delete(f"/language/{language_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Language deleted"

#Tests for Preferred_Attributes
def test_get_preferred_attribute():
    response = client.get("/preferred-attribute")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_preferred_attribute_by_profile_id():
    profile_id = 1  # Replace with a valid profile ID
    response = client.get(f"/preferred-attribute/{profile_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_insert_preferred_attribute():
    preferred_attribute_info = {
        "profile_id": 1,  # Replace with a valid profile ID
        "attribute_id": 1  # Replace with a valid attribute ID
    }
    response = client.post("/preferred-attribute", json=preferred_attribute_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Preferred attribute inserted"

def test_update_preferred_attributes():
    profile_id = 1  # Replace with a valid profile ID
    attribute_id = 1  # Replace with a valid attribute ID
    preferred_attribute_info = {
        "new_profile_id": 2,  # Replace with a valid new profile ID
        "new_attribute_id": 2  # Replace with a valid new attribute ID
    }
    response = client.put(f"/preferred-attribute/{profile_id}-{attribute_id}", json=preferred_attribute_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Preferred attribute updated"

def test_delete_preferred_attribute():
    profile_id = 1  # Replace with a valid profile ID
    attribute_id = 1  # Replace with a valid attribute ID
    response = client.delete(f"/preferred-attribute/{profile_id}-{attribute_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Preferred attribute deleted"

#Tests for profiles
def test_get_profile():
    response = client.get("/profile")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_profile_by_id():
    profile_id = 1  # Replace with a valid profile ID
    response = client.get(f"/profile/{profile_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_insert_profile():
    profile_info = {
        "user_id": 1,  # Replace with a valid user ID
        "age": 30,  # Replace with a valid age
        "nick_name": "test_user",  # Replace with a valid nick name
        "profile_picture": "test.jpg"  # Replace with a valid file name
    }
    response = client.post("/profile", json=profile_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Profile inserted"

def test_update_profile():
    profile_id = 1  # Replace with a valid profile ID
    profile_info = {
        "user_id": 1,  # Replace with a valid user ID
        "age": 35,  # Replace with a valid age
        "nick_name": "updated_user",  # Replace with an updated nick name
        "profile_picture": "updated.jpg"  # Replace with an updated file name
    }
    response = client.put(f"/profile/{profile_id}", json=profile_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated"

def test_delete_profile():
    profile_id = 1  # Replace with a valid profile ID
    response = client.delete(f"/profile/{profile_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Profile deleted"

#Tests for quality
def test_get_quality():
    response = client.get("/quality")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_get_quality_by_id():
    quality_id = 1  # Replace with a valid quality ID
    response = client.get(f"/quality/{quality_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "200 OK"
    assert len(response.json()["data"]) > 0

def test_insert_quality():
    quality_info = {
        "quality_type": "HD"  # Replace with a valid quality type
    }
    response = client.post("/quality", json=quality_info)
    assert response.status_code == 201
    assert response.json()["message"] == "Quality inserted"

def test_update_quality():
    quality_id = 1  # Replace with a valid quality ID
    quality_info = {
        "quality_type": "Full HD"  # Replace with an updated quality type
    }
    response = client.put(f"/quality/{quality_id}", json=quality_info)
    assert response.status_code == 200
    assert response.json()["message"] == "Quality updated"

def test_delete_quality():
    quality_id = 1  # Replace with a valid quality ID
    response = client.delete(f"/quality/{quality_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Quality deleted"
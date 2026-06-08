from fastapi.testclient import TestClient
from app.main import app
import uuid
import pytest

client = TestClient(app)

@pytest.fixture
def auth_token():
    email = f"routine_{uuid.uuid4()}@test.com"
    
    client.post("/auth/register", json={
        "name": "Yair",
        "email": email,
        "password": "123456"
    })
    
    login = client.post("/auth/login", data={
        "username": email,
        "password": "123456"
    })
    
    return login.json()["access_token"]

@pytest.fixture
def created_routine(auth_token):
    response = client.post(
        "/routines/",
        json={
            "name": "Push Day",
            "description": "rutina de empuje",
            "difficulty": "intermedia"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    return response.json()

def test_app_runs():
    response = client.get("/docs")
    assert response.status_code == 200
    
def test_register_user():
    email = f"yair_{uuid.uuid4()}@test.com"
    
    response = client.post(
        "/auth/register",
        json={
            "name": "Yair",
            "email": email,
            "password": "123456"
        }
    )
    
    assert response.status_code == 200
    
def test_register_duplicate_email():
    email = f"duplicate_{uuid.uuid4()}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Yair",
            "email": email,
            "password": "123456"
        }
    )

    response = client.post(
        "/auth/register",
        json={
            "name": "Yair",
            "email": email,
            "password": "123456"
        }
    )

    assert response.status_code == 409
    
def test_login_user():
    email = f"login_{uuid.uuid4()}@test.com"

    client.post(
        "/auth/register",
        json={
            "name": "Yair",
            "email": email,
            "password": "123456"
        }
    )
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "123456"
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
def test_me_user():
    email = f"test_{uuid.uuid4()}@test.com"
    
    client.post(
        "/auth/register",
        json={
            "name": "yair",
            "email": email,
            "password": "123456"
        }
    )
    
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "123456"
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"
    
    token = response.json()["access_token"]
    
    response_me = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    
    assert response_me.status_code == 200
    assert response_me.json()["email"] == email
    assert response_me.json()["name"] == "yair"
    
def test_me_without_token():
    response = client.get("/auth/me")
    
    assert response.status_code == 401
    
def test_create_routine(auth_token, created_routine):
    
    assert created_routine["name"] == "Push Day"
    
def test_create_routine_without_token():
    response = client.post(
        "/routines/",
        json={
            "name": "Push Day",
            "description": "Rutina de empuje",
            "difficulty": "intermedia"
        }
    )
    
    assert response.status_code == 401
    
def test_get_routines(auth_token, created_routine):
    response = client.get(
        "/routines/",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Push Day"
    
def test_get_routines_id(auth_token, created_routine):
    routine_id = created_routine["id"]
    
    response = client.get(
        f"/routines/{routine_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Push Day"
    
def test_put_routines_id(auth_token, created_routine):
    routine_id = created_routine["id"]
    
    response = client.put(
        f"/routines/{routine_id}",
        json={
            "name": "Pull Day",
            "description": "rutina de empuje",
            "difficulty": "avanzada"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Pull Day"
    assert response.json()["difficulty"] == "avanzada"
    assert response.json()["id"] == routine_id
    
def test_delete_routine(auth_token, created_routine):
    routine_id = created_routine["id"]
    
    response_delete = client.delete(
        f"/routines/{routine_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response_delete.status_code == 204
    
    response = client.get(
        f"/routines/{routine_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 404
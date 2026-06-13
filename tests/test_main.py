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
    
    return response

@pytest.fixture
def created_exercise():
    response = client.post(
        "/exercises",
        json={
            "name": "press banca",
            "muscle_group": "pecho",
            "equipment": "barra, banco",
            "instructions": "realizar con peso moderado"
        }
    )
    
    return response

@pytest.fixture
def created_routine_exercise(auth_token, created_exercise, created_routine):
    routine = created_routine.json()
    exercise = created_exercise.json()
    
    response = client.post(
        f"/routines/{routine['id']}/exercises",
        json={
            "exercise_id": exercise["id"],
            "sets": 4,
            "reps": 8,
            "rest_seconds": 180,
            "exercise_order": 1
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    return {
        "response": response,
        "routine": routine,
        "exercise": exercise
    }

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
    
def test_create_routine(created_routine):
    assert created_routine.status_code == 201
    assert created_routine.json()["id"] > 0
    assert created_routine.json()["name"] == "Push Day"
    assert created_routine.json()["description"] == "rutina de empuje"
    assert created_routine.json()["difficulty"] == "intermedia"
    
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
    routine_id = created_routine.json()["id"]
    
    response = client.get(
        f"/routines/{routine_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["name"] == "Push Day"
    
def test_put_routines_id(auth_token, created_routine):
    routine_id = created_routine.json()["id"]
    
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
    routine_id = created_routine.json()["id"]
    
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
    
def test_create_exercise(created_exercise):
    assert created_exercise.status_code == 201
    assert created_exercise.json()["name"] == "press banca"
    assert created_exercise.json()["muscle_group"] == "pecho"
    assert created_exercise.json()["equipment"] == "barra, banco"
    assert created_exercise.json()["instructions"] == "realizar con peso moderado"
    
def test_get_exercises(created_exercise):
    exercise_id = created_exercise.json()["id"]
    response = client.get(
        "/exercises"
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert response.json()[0]["name"] == "press banca"
    
def test_get_exercise_id(created_exercise):
    exercise_id = created_exercise.json()["id"]
    
    response = client.get(
        f"/exercises/{exercise_id}"
    )
    assert response.status_code == 200
    assert response.json()["name"] == "press banca"
    
def test_put_exercise_id(created_exercise):
    exercise_id = created_exercise.json()["id"]
    
    response = client.put(
        f"/exercises/{exercise_id}",
        json={
            "name": "press banca",
            "muscle_group": "pecho",
            "equipment": "barra, mancuernas, banco",
            "instructions": "realizar con peso moderado"
        }
    )
    assert response.status_code == 200
    assert response.json()["id"] == exercise_id
    assert response.json()["name"] == "press banca"
    assert response.json()["muscle_group"] == "pecho"
    assert response.json()["equipment"] == "barra, mancuernas, banco"
    assert response.json()["instructions"] ==  "realizar con peso moderado"
    
def test_delete_exercise_id(created_exercise):
    exercise_id = created_exercise.json()["id"]
    
    response = client.delete(
        f"/exercises/{exercise_id}"
    )
    response_get = client.get(
        f"/exercises/{exercise_id}"
    )
    assert response.status_code == 204
    assert response_get.status_code == 404
       
def test_get_exercise_not_found():
    response = client.get(
        "/exercises/999999"
    )
    assert response.status_code == 404
    
def test_put_exercise_not_found():
    response = client.put(
        "/exercises/999999",
        json={
            "name": "press banca",
            "muscle_group": "pecho",
            "equipment": "barra, mancuernas, banco",
            "instructions": "realizar con peso moderado"
        }
    )
    assert response.status_code == 404

def test_delete_exercise_not_found():
    response = client.delete(
        "/exercises/999999"
    )
    
    assert response.status_code == 404

def test_add_exercise_to_routine(created_routine_exercise):
    routine_id = created_routine_exercise["routine"]["id"]
    exercise_id = created_routine_exercise["exercise"]["id"]
    
    assert created_routine_exercise["response"].status_code == 201
    assert created_routine_exercise["response"].json()["routine_id"] == routine_id
    assert created_routine_exercise["response"].json()["exercise_id"] == exercise_id
    assert created_routine_exercise["response"].json()["sets"] == 4
    assert created_routine_exercise["response"].json()["reps"] == 8
    assert created_routine_exercise["response"].json()["rest_seconds"] == 180
    assert created_routine_exercise["response"].json()["exercise_order"] == 1
    
def test_add_exercise_to_routine_duplicate(auth_token, created_routine_exercise):
    routine_id = created_routine_exercise["routine"]["id"]
    exercise_id = created_routine_exercise["exercise"]["id"]
    
    response = client.post(
        f"/routines/{routine_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "sets": 4,
            "reps": 8,
            "rest_seconds": 180,
            "exercise_order": 1
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "este ejercicio ya esta agregado en la rutina"
    
def test_add_exercise_to_routine_invalid_routine(auth_token, created_routine_exercise):
    exercise_id = created_routine_exercise["exercise"]["id"]
    
    response = client.post(
        f"/routines/{999999}/exercises",
        json={
            "exercise_id": exercise_id,
            "sets": 4,
            "reps": 8,
            "rest_seconds": 180,
            "exercise_order": 1
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "rutina no encontrada"
    
def test_add_exercise_to_routine_invalid_exercise(auth_token, created_routine_exercise):
    routine_id = created_routine_exercise["routine"]["id"]
    
    response = client.post(
        f"/routines/{routine_id}/exercises",
        json={
            "exercise_id": 999999,
            "sets": 4,
            "reps": 8,
            "rest_seconds": 180,
            "exercise_order": 1
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "ejercicio no encontrado"

def test_get_routine_exercises(auth_token ,created_routine_exercise):
    routine_id = created_routine_exercise["routine"]["id"]
    routine_exercise_id = created_routine_exercise["response"].json()["id"]
    
    response = client.get(
        f"/routines/{routine_id}/exercises",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert any(
        item["id"] == routine_exercise_id
        and item["routine_id"] == routine_id
        for item in response.json()
    )
    
def test_put_routine_exercise(auth_token, created_routine_exercise):
    routine_id = created_routine_exercise["routine"]["id"]
    routine_exercise_id = created_routine_exercise["response"].json()["id"]
    exercise_id = created_routine_exercise["exercise"]["id"]
    
    response = client.put(
        f"/routines/{routine_id}/exercises/{routine_exercise_id}",
        json={
            "exercise_id": exercise_id,
            "sets": 3,
            "reps": 6,
            "rest_seconds": 180,
            "exercise_order": 1
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["exercise_id"] == exercise_id
    assert response.json()["sets"] == 3
    assert response.json()["reps"] == 6
    assert response.json()["rest_seconds"] == 180
    assert response.json()["exercise_order"] == 1
    
def test_delete_routine_exercise(auth_token, created_routine_exercise):
    routine_id = created_routine_exercise["routine"]["id"]
    routine_exercise_id = created_routine_exercise["response"].json()["id"]
    
    response = client.delete(
        f"/routines/{routine_id}/exercises/{routine_exercise_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    response_get = client.get(
        f"/routines/{routine_id}/exercises/{routine_exercise_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 204
    assert response_get.status_code == 404
    assert response_get.json()["detail"] == "ejercicio no encontrado"
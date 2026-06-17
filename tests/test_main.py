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
    
@pytest.fixture
def created_workout(auth_token ,created_routine_exercise):
    routine_id = created_routine_exercise["routine"]["id"]
    exercise_id = created_routine_exercise["exercise"]["id"]
    
    response = client.post(
        "/workouts",
        json={
            "routine_id": routine_id,
            "notes": "molestia leve en el hombro"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    return {
        "response": response,
        "workout": response.json(),
        "routine_id": routine_id,
        "exercise_id": exercise_id
    }
    
@pytest.fixture
def created_workout_exercise(auth_token ,created_workout):
    workout_id = created_workout["response"].json()["id"]
    exercise_id = created_workout["exercise_id"]
    
    response = client.post(
        f"/workouts/{workout_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "sets_completed": 4,
            "reps_completed": 8,
            "weight": 100,
            "notes": "me senti fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    return {
        "response": response,
        "workout_id": workout_id,
        "exercise_id": exercise_id
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
    
def test_create_workout(created_workout):
    assert created_workout["response"].status_code == 201
    assert created_workout["response"].json()["routine_id"] == created_workout["routine_id"]
    
def test_create_workout_invalid_routine(auth_token, created_routine_exercise):
    response = client.post(
        "/workouts",
        json={
            "routine_id": 999999,
            "notes": "molestia leve en el hombro"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "rutina no encontrada"
    
def test_create_workout_duplicate_active(auth_token ,created_workout):
    routine_id = created_workout["routine_id"]
    
    response = client.post(
        "/workouts",
        json={
            "routine_id": routine_id,
            "notes": "molestia leve en el hombro"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Ya tienes un entrenamiento"
    
def test_put_finish_workout(auth_token ,created_workout):
    workout_id = created_workout["workout"]["id"]
    
    response = client.put(
        f"/workouts/{workout_id}/finish",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == workout_id
    assert response.json()["finished_at"] is not None
    
def test_put_finish_invalid_workout(auth_token, created_workout):
    response = client.put(
        f"/workouts/{999999}/finish",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "entrenamiento no encontrado"
    
def test_put_finish_duplicate_workout(auth_token, created_workout):
    workout_id = created_workout["workout"]["id"]
    
    client.put(
        f"/workouts/{workout_id}/finish",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    response = client.put(
        f"/workouts/{workout_id}/finish",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "el entrenamiento ya fue finalizado"
    
def test_get_workouts(auth_token ,created_workout):
    workout_id = created_workout["workout"]["id"]
    
    response = client.get(
        "/workouts",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert any(
        workout["id"] == workout_id
        for workout in response.json()
    )
    
def test_add_exercise_to_workout(created_workout_exercise):
    assert created_workout_exercise["response"].status_code == 201
    assert created_workout_exercise["response"].json()["workout_session_id"] == created_workout_exercise["workout_id"]
    assert created_workout_exercise["response"].json()["sets_completed"] == 4
    assert created_workout_exercise["response"].json()["reps_completed"] == 8
    assert created_workout_exercise["response"].json()["weight"] == 100
    assert created_workout_exercise["response"].json()["notes"] == "me senti fuerte"

def test_add_exercise_to_invalid_workout(auth_token, created_workout):
    exercise_id = created_workout["exercise_id"]
    
    response = client.post(
        f"/workouts/{999999}/exercises",
        json={
            "exercise_id": exercise_id,
            "sets_completed": 4,
            "reps_completed": 8,
            "weight": 100,
            "notes": "me senti fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "entrenamiento no encontrado"

def test_add_exercise_to_finished_workout(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    exercise_id = created_workout_exercise["exercise_id"]
    
    client.put(
        f"/workouts/{workout_id}/finish",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    response = client.post(
        f"/workouts/{workout_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "sets_completed": 4,
            "reps_completed": 8,
            "weight": 100,
            "notes": "me senti fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "el entrenamiento ya fue finalizado"
    
def test_add_invalid_exercise_to_workout(auth_token, created_workout):
    workout_id = created_workout["response"].json()["id"]
    
    response = client.post(
        f"/workouts/{workout_id}/exercises",
        json={
            "exercise_id": 999999,
            "sets_completed": 4,
            "reps_completed": 8,
            "weight": 100,
            "notes": "me senti fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 404
    assert response.json()["detail"] == "ejercicio no encontrado"

def test_add_no_belong_exercise_to_workout(auth_token, created_workout):
    workout_id = created_workout["response"].json()["id"]
    
    response_exercise = client.post(
        "/exercises",
        json={
            "name": "pull over",
            "muscle_group": "espalda",
            "equipment": "polea",
            "instructions": "realizar con peso moderado"
        }
    )
    
    assert response_exercise.status_code == 201
    
    exercise_id = response_exercise.json()["id"]
    
    response = client.post(
        f"/workouts/{workout_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "sets_completed": 4,
            "reps_completed": 8,
            "weight": 100,
            "notes": "me senti fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "este ejercicio no pertenece a la rutina del entrenamiento"
    
def test_add_duplicate_exercise_to_workout(auth_token ,created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    exercise_id = created_workout_exercise["exercise_id"]
    
    response = client.post(
        f"/workouts/{workout_id}/exercises",
        json={
            "exercise_id": exercise_id,
            "sets_completed": 4,
            "reps_completed": 8,
            "weight": 100,
            "notes": "me senti fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "el ejercicio ya fue registrado en este entrenamiento"
    
def test_get_workouts_stats(auth_token ,created_workout_exercise):
    response = client.get(
        "/workouts/stats",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 200
    assert "total_workouts" in response.json()
    assert "total_exercises" in response.json()
    assert "average_duration_minutes" in response.json()
    assert "total_weight_lifted" in response.json()
    
def test_get_workout_id_detail(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    
    response = client.get(
        f"/workouts/{workout_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["id"] == workout_id
    assert response.json()["routine_id"] is not None
    
def test_get_workout_not_found(auth_token, created_workout_exercise):
    response = client.get(
        f"/workouts/{999999}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "entrenamiento no encontrado"
    
def test_get_workout_exercises(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    
    response = client.get(
        f"/workouts/{workout_id}/exercises",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    
    assert response.status_code == 200
    assert any(
        item["id"] == workout_exercise_id
        for item in response.json()
    )
    
def test_get_workout_exercises_invalid_workout(auth_token, created_workout_exercise):
    response = client.get(
        f"/workouts/{999999}/exercises",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "entrenamiento no encontrado"
    
def test_get_workout_exercise_id(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    
    response = client.get(
        f"/workouts/{workout_id}/exercises/{workout_exercise_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["id"] == created_workout_exercise["response"].json()["id"]
    
def test_get_workout_exercise_invalid_workout(auth_token, created_workout_exercise):
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    
    response = client.get(
        f"/workouts/{999999}/exercises/{workout_exercise_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "entrenamiento no encontrado"
    
def test_get_workout_exercise_not_found(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]

    response = client.get(
        f"/workouts/{workout_id}/exercises/{999999}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "ejercicio no encontrado"
    
def test_delete_workout_exercise(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    
    response = client.delete(
        f"/workouts/{workout_id}/exercises/{workout_exercise_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    response_get = client.get(
        f"/workouts/{workout_id}/exercises/{workout_exercise_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 204
    assert response_get.status_code == 404
    assert response_get.json()["detail"] == "ejercicio no encontrado"
    
def test_delete_workout_exercise_invalid_workout(auth_token, created_workout_exercise):
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    
    response = client.delete(
        f"/workouts/{999999}/exercises/{workout_exercise_id}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "entrenamiento no encontrado"
    
def test_delete_workout_exercise_not_found(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]

    response = client.delete(
        f"/workouts/{workout_id}/exercises/{999999}",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "ejercicio no encontrado"
    
def test_put_workout_exercise(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    exercise_id = created_workout_exercise["exercise_id"]
    
    response = client.put(
        f"/workouts/{workout_id}/exercises/{workout_exercise_id}",
        json={
            "sets_completed": 3,
            "reps_completed": 10,
            "weight": 120,
            "notes": "me senti mas fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["id"] == created_workout_exercise["response"].json()["id"]
    assert response.json()["exercise_id"] == exercise_id
    assert response.json()["sets_completed"] == 3
    assert response.json()["reps_completed"] == 10
    assert response.json()["weight"] == 120
    assert response.json()["notes"] == "me senti mas fuerte"

def test_put_workout_exercise_invalid_workout(auth_token, created_workout_exercise):
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    
    response = client.put(
        f"/workouts/{999999}/exercises/{workout_exercise_id}",
        json={
            "sets_completed": 3,
            "reps_completed": 10,
            "weight": 120,
            "notes": "me senti mas fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "entrenamiento no encontrado"
    
def test_put_workout_exercise_finished(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    workout_exercise_id = created_workout_exercise["response"].json()["id"]
    
    client.put(
        f"/workouts/{workout_id}/finish",
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    response = client.put(
        f"/workouts/{workout_id}/exercises/{workout_exercise_id}",
        json={
            "sets_completed": 3,
            "reps_completed": 10,
            "weight": 120,
            "notes": "me senti mas fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "el entrenamiento ya fue finalizado"
    
def test_put_workout_exercise_not_found(auth_token, created_workout_exercise):
    workout_id = created_workout_exercise["workout_id"]
    
    response = client.put(
        f"/workouts/{workout_id}/exercises/{999999}",
        json={
            "sets_completed": 3,
            "reps_completed": 10,
            "weight": 120,
            "notes": "me senti mas fuerte"
        },
        headers={
            "Authorization": f"Bearer {auth_token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "ejercicio no encontrado"
    
    
# Gym Routine API

API REST desarrollada con FastAPI para gestionar usuarios, rutinas y ejercicios.

## Tecnologías

- Python
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- JWT
- Pydantic

## Características

- Registro de usuarios
- Login con JWT
- CRUD de rutinas
- CRUD de ejercicios
- Relación rutina-ejercicio

## Instalación

```bash
git clone https://github.com/yaircarpin/gym_routine_api.git

cd gym_routine_api

python -m venv .venv

pip install -r requirements.txt
```

## Variables de entorno

```env
DATABASE_URL=
SECRET_KEY=
ALGORITHM=
ACCESS_TOKEN_EXPIRE_MINUTES=
```

## Ejecutar proyecto

```bash
uvicorn app.main:app --reload
```
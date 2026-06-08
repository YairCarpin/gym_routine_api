from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import get_db, Base
from app.main import app
from app.config import TEST_DATABASE_URL
from app import models

engine_test = create_engine(TEST_DATABASE_URL)

# TODO: reemplazar por Alembic cuando las migraciones estén corregidas
Base.metadata.create_all(bind=engine_test)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
app.dependency_overrides[get_db] = override_get_db
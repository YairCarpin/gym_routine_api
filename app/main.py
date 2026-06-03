from fastapi import FastAPI
from app.database import engine, Base
from app.routers import auth, routines, exercises, workouts

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(routines.router)
app.include_router(exercises.router)
app.include_router(workouts.router)



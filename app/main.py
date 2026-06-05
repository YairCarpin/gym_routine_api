from fastapi import FastAPI
from app.routers import auth, routines, exercises, workouts

app = FastAPI()

app.include_router(auth.router)
app.include_router(routines.router)
app.include_router(exercises.router)
app.include_router(workouts.router)



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas import ExerciseCreate, ExerciseResponse
from app.database import get_db
from app import models

router = APIRouter(
    prefix="/exercises",
    tags=["Exercises"]
)

@router.post(
    "/",
    response_model=ExerciseResponse
)
async def add_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db)
):
    new_exercise = models.Exercise(
        name=exercise.name,
        muscle_group=exercise.muscle_group,
        equipment=exercise.equipment,
        instructions=exercise.instructions
    )
    
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    
    return new_exercise

@router.get(
    "/",
    response_model=list[ExerciseResponse]
)
async def get_exercises(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    
    stmt = (
        select(models.Exercise)
        .offset(skip)
        .limit(limit)
    )
    exercises_db = db.scalars(stmt).all()
    
    return exercises_db

@router.get(
    "/{exercise_id}",
    response_model=ExerciseResponse
)
async def return_exercise(
    exercise_id: int,
    db: Session = Depends(get_db)
):
    stmt = select(models.Exercise).where(
        models.Exercise.id == exercise_id
    )
    
    exercise_db = db.execute(stmt).scalar_one_or_none()
    
    if exercise_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio no encontrado"
        )
        
    return exercise_db
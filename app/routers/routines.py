from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.schemas import (
    RoutineCreate, RoutineResponse, RoutineExerciseCreate,
    RoutineExerciseResponse, RoutineExerciseDetailResponse,
)
from app.database import get_db
from app.dependencies.auth import get_current_user
from app import models

router = APIRouter(
    prefix="/routines",
    tags=["Routines"]
)

@router.post(
    "/",
    response_model=RoutineResponse
)
async def routines(
    routine: RoutineCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_routine = models.Routine (
        name=routine.name,
        difficulty=routine.difficulty,
        description=routine.description,
        user_id=current_user.id
    )
    
    db.add(new_routine)
    db.commit()
    db.refresh(new_routine)
    
    return new_routine

@router.get(
    "/",
    response_model=list[RoutineResponse]
)
async def get_routines(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(
        models.Routine.user_id == current_user.id
    )
    routines_db = db.scalars(stmt).all()
    
    return routines_db

@router.get(
    "/{routine_id}",
    response_model=RoutineResponse
)
async def return_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(
        models.Routine.id == routine_id,
        models.Routine.user_id == current_user.id
    )
    
    routine_db = db.execute(stmt).scalar_one_or_none()
    
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
    
    return routine_db
    
@router.put(
    "/{routine_id}",
    response_model=RoutineResponse
)
async def modify_routine(
    routine: RoutineCreate,
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    stmt = select(models.Routine).where(
        models.Routine.id == routine_id,
        models.Routine.user_id == current_user.id,           
    )
    
    routine_db = db.execute(stmt).scalar_one_or_none()
    
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
    
    routine_db.name=routine.name
    routine_db.difficulty=routine.difficulty
    routine_db.description=routine.description
    
    db.commit()
    db.refresh(routine_db)
    return routine_db
    
@router.delete(
    "/{routine_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    
    stmt = select(models.Routine).where(
        models.Routine.id == routine_id,
        models.Routine.user_id == current_user.id           
    )
        
    routine_db = db.execute(stmt).scalar_one_or_none()
    
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
    
    db.delete(routine_db)
    
    db.commit()

@router.post(
    "/{routine_id}/exercises",
    response_model=RoutineExerciseResponse
)
async def add_exercise_to_routine(
    routine_id: int,
    routine_exercise: RoutineExerciseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(
        models.Routine.id == routine_id,
        models.Routine.user_id == current_user.id
    )
    
    routine_db = db.execute(stmt).scalar_one_or_none()
        
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
        
    stmt_exercise = select(models.Exercise).where(
        models.Exercise.id == routine_exercise.exercise_id
    )
    
    exercise_db = db.execute(stmt_exercise).scalar_one_or_none()
        
    if exercise_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio no encontrado"
        )
    
    stmt_duplicate = select(models.RoutineExercise).where(
        models.RoutineExercise.routine_id == routine_id,
        models.RoutineExercise.exercise_id == routine_exercise.exercise_id
    )
    
    duplicate = db.execute(stmt_duplicate).scalar_one_or_none()
    
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="este ejercicio ya esta agregado en la rutina"
        )
    
    new_routine_exercise = models.RoutineExercise(
        routine_id=routine_id,
        exercise_id=routine_exercise.exercise_id,
        sets=routine_exercise.sets,
        reps=routine_exercise.reps,
        rest_seconds=routine_exercise.rest_seconds,
        exercise_order=routine_exercise.exercise_order
    )
    
    db.add(new_routine_exercise)
    db.commit()
    db.refresh(new_routine_exercise)
    
    return new_routine_exercise

@router.get(
    "/{routine_id}/exercises",
    response_model=list[RoutineExerciseDetailResponse]
)
async def exercises_routine(
    routine_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(
        models.Routine.id == routine_id,
        models.Routine.user_id == current_user.id
    )
    
    routine_db = db.execute(stmt).scalar_one_or_none()
    
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
        
    stmt_routine_exercise = select(models.RoutineExercise).where(
        models.RoutineExercise.routine_id == routine_id
    )
    
    routine_exercises_db = db.scalars(stmt_routine_exercise).all()
    
    return routine_exercises_db

@router.delete(
    "/{routine_id}/exercises/{routine_exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_routine_exercise(
    routine_id: int,
    routine_exercise_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(
        models.Routine.id == routine_id,
        models.Routine.user_id == current_user.id           
    )
        
    routine_db = db.execute(stmt).scalar_one_or_none()
    
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
    
    stmt_routine_exercise = select(models.RoutineExercise).where(
        models.RoutineExercise.routine_id == routine_id,
        models.RoutineExercise.id == routine_exercise_id,
    )
    
    routine_exercise_db = db.execute(stmt_routine_exercise).scalar_one_or_none()
    
    if routine_exercise_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio no encontrado"
        )
        
    db.delete(routine_exercise_db)
    
    db.commit()
    
@router.put(
    "/{routine_id}/exercises/{routine_exercise_id}",
    response_model=RoutineExerciseResponse
)
async def update_routine_exercise(
    routine_id: int,
    routine_exercise_id: int,
    routine_exercise: RoutineExerciseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(
        models.Routine.id == routine_id,
        models.Routine.user_id == current_user.id
    )
    
    routine_db = db.execute(stmt).scalar_one_or_none()
    
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
        
    stmt_routine_exercise = select(models.RoutineExercise).where(
        models.RoutineExercise.routine_id == routine_id,
        models.RoutineExercise.id == routine_exercise_id
    )
    
    routine_exercise_db = db.execute(stmt_routine_exercise).scalar_one_or_none()
    
    if routine_exercise_db == None:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio de rutina no encontrado"
        )
    
    stmt_exercise = select(models.Exercise).where(
        models.Exercise.id == routine_exercise.exercise_id
    )
    
    exercise_db = db.execute(stmt_exercise).scalar_one_or_none()
        
    if exercise_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio no encontrado"
        )
    
    routine_exercise_db.exercise_id = routine_exercise.exercise_id
    routine_exercise_db.sets = routine_exercise.sets
    routine_exercise_db.reps = routine_exercise.reps
    routine_exercise_db.rest_seconds = routine_exercise.rest_seconds
    routine_exercise_db.exercise_order = routine_exercise.exercise_order
    
    db.commit()
    db.refresh(routine_exercise_db)
    
    return routine_exercise_db
        
    
    
    
    
    
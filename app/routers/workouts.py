from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.schemas import (
    WorkoutSessionCreate, WorkoutSessionResponse,
    WorkoutExerciseCreate, WorkoutExerciseResponse,
    WorkoutSessionDetailResponse, WorkoutExerciseDetailResponse,
    WorkoutExerciseUpdate
)
from app.database import get_db
from app.dependencies.auth import get_current_user
from app import models
from datetime import datetime, UTC

router = APIRouter(
    prefix="/workouts",
    tags=["workouts"]
)

@router.post(
    "/",
    response_model=WorkoutSessionResponse
)
async def verify_routine(
    workout_session: WorkoutSessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(
        models.Routine.id == workout_session.routine_id,
        models.Routine.user_id == current_user.id
    )
    
    routine_db = db.execute(stmt).scalar_one_or_none()
    
    if routine_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="rutina no encontrada"
        )
    
    stmt_active = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.finished_at == None
    )
    
    workout_session_db = db.execute(stmt_active).scalar_one_or_none()
    
    if workout_session_db != None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya tienes un entrenamiento"
        )
        
    new_workout_session = models.WorkoutSession(
        user_id = current_user.id,
        routine_id = workout_session.routine_id,
        notes = workout_session.notes
    )
    
    db.add(new_workout_session)
    db.commit()
    db.refresh(new_workout_session)
    
    return new_workout_session

@router.put(
    "/{workout_id}/finish",
    response_model=WorkoutSessionResponse
)
async def finish_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.id == workout_id
    )
    
    workout_db = db.execute(stmt).scalar_one_or_none()
    
    if workout_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="entrenamiento no encontrado"
        )
        
    if workout_db.finished_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el entrenamiento ya fue finalizado"
        )
        
    workout_db.finished_at = datetime.now(UTC)
    
    db.commit()
    db.refresh(workout_db)
    
    return workout_db
    
@router.get(
    "/",
    response_model=list[WorkoutSessionResponse]
)
async def workouts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
    )
    
    workouts_db = db.scalars(stmt).all()
    
    return workouts_db

@router.post(
    "/{workout_id}/exercises",
    response_model=WorkoutExerciseResponse
)
async def exercises (
    workout_id: int,
    workout_exercise: WorkoutExerciseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.id == workout_id
    )
    
    workout_db = db.execute(stmt).scalar_one_or_none()
    
    if workout_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="entrenamiento no encontrado"
        )
        
    if workout_db.finished_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el entrenamiento ya fue finalizado"
        )
    
    stmt_exercise = select(models.Exercise).where(
        models.Exercise.id == workout_exercise.exercise_id
    )
    
    exercise_db = db.execute(stmt_exercise).scalar_one_or_none()
    
    if exercise_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio no encontrado"
        )
    
    stmt_routine_exercise = select(models.RoutineExercise).where(
        models.RoutineExercise.routine_id == workout_db.routine_id,
        models.RoutineExercise.exercise_id == workout_exercise.exercise_id
    )
    
    routine_exercise_db = db.execute(stmt_routine_exercise).scalar_one_or_none()
    
    if routine_exercise_db is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="este ejercicio no pertenece a la rutina del entrenamiento"
        )
    
    stmt_duplicate = select(models.WorkoutExercise).where(
        models.WorkoutExercise.workout_session_id == workout_id,
        models.WorkoutExercise.exercise_id == workout_exercise.exercise_id
    )
    
    duplicate_db = db.execute(stmt_duplicate).scalar_one_or_none()
    
    if duplicate_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el ejercicio ya fue registrado en este entrenamiento"
        )
        
    new_workout_exercise = models.WorkoutExercise(
        workout_session_id = workout_id,
        exercise_id = workout_exercise.exercise_id,
        sets_completed = workout_exercise.sets_completed,
        reps_completed = workout_exercise.reps_completed,
        weight = workout_exercise.weight,
        notes = workout_exercise.notes
    )
    
    db.add(new_workout_exercise)
    db.commit()
    db.refresh(new_workout_exercise)
    
    return new_workout_exercise

@router.get(
    "/active",
    response_model=WorkoutSessionResponse
)
async def workout_active(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.finished_at == None
    )
    
    workout_db = db.execute(stmt).scalar_one_or_none()
    
    if workout_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay entrenamiento activo"
        )
        
    return workout_db
    
@router.get(
    "/{workout_id}",
    response_model=WorkoutSessionDetailResponse
)
async def get_workout_detail(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.id == workout_id
    )
    
    workout_db = db.execute(stmt).scalar_one_or_none()
    
    if workout_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="entrnamiento no encontrado"
        )
    
    return workout_db

@router.get(
    "/{workout_id}/exercises",
    response_model=list[WorkoutExerciseResponse]
)
async def workout_exercises(
    workout_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.id == workout_id
    )
    
    workout_db = db.execute(stmt).scalar_one_or_none()
    
    if workout_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="entrenamiento no encontrado"
        )
        
    stmt_workout_exercise = select(models.WorkoutExercise).where(
        models.WorkoutExercise.workout_session_id == workout_id
    )
    
    workout_exercise_db = db.scalars(stmt_workout_exercise).all()
    
    return workout_exercise_db

@router.delete(
    "/{workout_id}/exercises/{workout_exercise_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_exercise(
    workout_id: int,
    workout_exercise_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.id == workout_id
    )
    
    workout_db = db.execute(stmt).scalar_one_or_none()
    
    if workout_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="entrenamieto no encontrado"
        )
        
    stmt_exercise = select(models.WorkoutExercise).where(
        models.WorkoutExercise.workout_session_id == workout_db.id,
        models.WorkoutExercise.id == workout_exercise_id
    )
    
    workout_exercise_db = db.execute(stmt_exercise).scalar_one_or_none()
    
    if workout_exercise_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio no encontrado"
        )
    
    db.delete(workout_exercise_db)
    db.commit()

@router.put(
    "/{workout_id}/exercises/{workout_exercise_id}",
    response_model=WorkoutExerciseResponse
)
async def put_workout_exercise(
    workout_exercise: WorkoutExerciseUpdate,
    workout_id: int,
    workout_exercise_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    stmt = select(models.WorkoutSession).where(
        models.WorkoutSession.user_id == current_user.id,
        models.WorkoutSession.id == workout_id
    )
    
    workout_db = db.execute(stmt).scalar_one_or_none()
    
    if workout_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="entrenamiento no encontrado"
        )
        
    if workout_db.finished_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="el entrenamiento ya fue finalizado"
        )
    
    stmt_exercise = select(models.WorkoutExercise).where(
        models.WorkoutExercise.workout_session_id == workout_id,
        models.WorkoutExercise.id == workout_exercise_id
    )
    
    workout_exercise_db = db.execute(stmt_exercise).scalar_one_or_none()
    
    if workout_exercise_db == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ejercicio no encontrado"
        )
        
    workout_exercise_db.sets_completed=workout_exercise.sets_completed
    workout_exercise_db.reps_completed=workout_exercise.reps_completed
    workout_exercise_db.weight=workout_exercise.weight
    workout_exercise_db.notes=workout_exercise.notes
    
    db.commit()
    db.refresh(workout_exercise_db)
    
    return workout_exercise_db
    
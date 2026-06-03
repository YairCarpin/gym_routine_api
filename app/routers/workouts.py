from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.schemas import WorkoutSessionCreate, WorkoutSessionResponse
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

@router.get(
    "/{workout_id}",
    response_model=WorkoutSessionResponse
)
async def workouts(
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
    
    return workout_db
        
    
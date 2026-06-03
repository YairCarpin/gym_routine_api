from sqlalchemy import create_engine, DateTime, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC

from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    email: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(250), nullable=False)
    
    routines = relationship("Routine", back_populates="user")
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    
class Routine(Base):
    __tablename__ = "routines"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user = relationship("User", back_populates="routines")
    routine_exercises = relationship("RoutineExercise", back_populates="routine")
    workout_sessions = relationship("WorkoutSession", back_populates="routine")
    
class Exercise(Base):
    __tablename__ = "exercises"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    muscle_group: Mapped[str] = mapped_column(String(50))
    equipment: Mapped[str] = mapped_column(String(100))
    
    routine_exercises = relationship("RoutineExercise", back_populates="exercise")
    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    
class RoutineExercise(Base):
    __tablename__ = "routine_exercises"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    routine_id: Mapped[int] = mapped_column(ForeignKey("routines.id"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    
    sets: Mapped[int] = mapped_column(Integer)
    reps: Mapped[int] = mapped_column(Integer)
    rest_seconds: Mapped[int] = mapped_column(Integer)
    exercise_order: Mapped[int] = mapped_column(Integer)   
    
    exercise = relationship("Exercise", back_populates="routine_exercises")
    routine = relationship("Routine", back_populates="routine_exercises")
    
class WorkoutSession(Base):
    __tablename__ = "workout_sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    routine_id: Mapped[int] = mapped_column(ForeignKey("routines.id"))
    
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC)
    )
    
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    notes: Mapped[str] = mapped_column(String(200), nullable=True)
    
    user = relationship("User", back_populates="workout_sessions")
    routine = relationship("Routine", back_populates="workout_sessions")
    workout_exercises = relationship("WorkoutExercise", back_populates="workout_sessions")

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    workout_session_id: Mapped[int] = mapped_column(ForeignKey("workout_sessions.id"))
    
    sets_completed: Mapped[int] = mapped_column(Integer)
    reps_completed: Mapped[int] = mapped_column(Integer)
    weight: Mapped[int] = mapped_column(Integer)
    notes: Mapped[str] = mapped_column(String(200), nullable=True)
     
    workout_sessions = relationship("WorkoutSession", back_populates="workout_exercises")   
    exercise = relationship("Exercise", back_populates="workout_exercises")
    
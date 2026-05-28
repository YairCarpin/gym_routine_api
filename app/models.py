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

class Routine(Base):
    __tablename__ = "routines"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(50), nullable=True)
    description: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    user = relationship("User", back_populates="routines")
    routine_exercises = relationship("RoutineExercise", back_populates="routine")
    
class Exercise(Base):
    __tablename__ = "exercises"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    muscle_group: Mapped[str] = mapped_column(String(50))
    equipment: Mapped[str] = mapped_column(String(100))
    
    routine_exercises = relationship("RoutineExercise", back_populates="exercise")
    
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
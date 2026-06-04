from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    email: EmailStr
    
class RoutineCreate(BaseModel):
    name: str
    description: str
    difficulty: str
    
class RoutineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    description: str
    difficulty: str
    
class ExerciseCreate(BaseModel):
    name: str
    muscle_group: str
    equipment: str
    
class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    name: str
    muscle_group: str
    equipment: str

class RoutineExerciseCreate(BaseModel):
    exercise_id: int
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    rest_seconds: int = Field(ge=0)
    exercise_order: int = Field(gt=0)
    
class RoutineExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    exercise_id: int
    sets: int
    reps: int
    rest_seconds: int
    exercise_order: int
    
class RoutineExerciseDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    exercise: ExerciseResponse
    sets: int
    reps: int
    rest_seconds: int
    exercise_order: int
    
class WorkoutSessionCreate(BaseModel):
    routine_id: int
    notes: str | None = None
    
class WorkoutSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    routine_id: int
    started_at: datetime
    finished_at: datetime | None
    notes: str | None
    
class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    sets_completed: int
    reps_completed: int
    weight: int
    notes: str | None = None
    
class WorkoutExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    exercise_id: int
    sets_completed: int
    reps_completed: int
    weight: int
    notes: str | None
    
class WorkoutExerciseDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    exercise: ExerciseResponse
    sets_completed: int
    reps_completed: int
    weight: int
    notes: str | None
    
class WorkoutSessionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    routine_id: int
    started_at: datetime
    finished_at: datetime | None
    notes: str | None
    workout_exercises: list[WorkoutExerciseDetailResponse]
    
class WorkoutExerciseUpdate(BaseModel):
    sets_completed: int
    reps_completed: int
    weight: int
    notes: str | None = None
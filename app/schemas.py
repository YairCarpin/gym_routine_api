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
    name: str = Field(min_length=3, max_length=80)
    description: str = Field(max_length=250)
    difficulty: str = Field(max_length=50)
    
class RoutineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: str
    difficulty: str
    
class ExerciseCreate(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    muscle_group: str = Field(min_length=3, max_length=50)
    equipment: str = Field(max_length=100)
    instructions: str | None = Field(default=None, max_length=250)
    
class ExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    muscle_group: str
    equipment: str
    instructions: str | None

class RoutineExerciseCreate(BaseModel):
    exercise_id: int = Field(gt=0)
    sets: int = Field(gt=0)
    reps: int = Field(gt=0)
    rest_seconds: int = Field(ge=0)
    exercise_order: int = Field(gt=0)
    
class RoutineExerciseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    routine_id: int
    exercise_id: int
    sets: int
    reps: int
    rest_seconds: int
    exercise_order: int
    
class RoutineExerciseDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    routine_id: int
    exercise: ExerciseResponse
    sets: int
    reps: int
    rest_seconds: int
    exercise_order: int
    
class WorkoutSessionCreate(BaseModel):
    routine_id: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=200)
    
class WorkoutSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    routine_id: int
    started_at: datetime
    finished_at: datetime | None
    notes: str | None
    
class WorkoutExerciseCreate(BaseModel):
    exercise_id: int = Field(gt=0)
    sets_completed: int = Field(gt=0)
    reps_completed: int = Field(gt=0)
    weight: int = Field(gt=0)
    notes: str | None = Field(default=None, max_length=200)
    
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
    sets_completed: int = Field(gt=0)
    reps_completed: int = Field(gt=0)
    weight: int = Field(ge=0)
    notes: str | None = Field(default=None, max_length=200)
    
class WorkoutStatsResponse(BaseModel):
    total_workouts: int
    total_exercises: int
    average_duration_minutes: float
    total_weight_lifted: int
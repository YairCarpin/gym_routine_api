from pydantic import BaseModel, EmailStr, ConfigDict, Field

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
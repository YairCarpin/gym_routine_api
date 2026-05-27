from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.database import engine, Base, SessionLocal
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app import models
from app.schemas import UserCreate, UserResponse, RoutineCreate, RoutineResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.utils.security import hash_password, verify_password
from jose import jwt, JWTError
import datetime


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    
    try:
        yield db
        
    finally:
        db.close()
        
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    stmt = select(models.User).where(models.User.email == email)
    user_db = db.execute(stmt).scalar_one_or_none()
    
    if user_db is None:
        raise credentials_exception
    
    return user_db

@app.get("/")
async def home():
    return {"message": "Api running"}

@app.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    new_user = models.User(
        name=user.name,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email = form_data.username
    password = form_data.password
    
    stmt = select(models.User).where(models.User.email == email)
    user_db = db.execute(stmt).scalar_one_or_none()
    
    if not user_db or not verify_password(password, user_db.hashed_password):
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="credenciales invalidas"
    )
        
    payload = {
        "sub": email,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    }
            
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer"
    }
    
@app.get("/me", response_model=UserResponse)
async def me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/routines", response_model=RoutineResponse)
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

@app.get("/routines", response_model=list[RoutineResponse])
async def get_routines(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    stmt = select(models.Routine).where(models.Routine.user_id == current_user.id)
    routines_db = db.scalars(stmt).all()
    
    return routines_db

@app.get("/routines/{routine_id}", response_model=RoutineResponse)
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
    
@app.put("/routines/{routine_id}", response_model=RoutineResponse)
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
    
    
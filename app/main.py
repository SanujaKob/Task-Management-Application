from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app import models, schemas, crud
from app.database import SessionLocal, engine
from app.auth import verify_password, create_access_token, get_current_user

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI()

# ✅ Add OAuth2 scheme so /docs gets the 🔐 Authorize button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Register a new user
@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)

# ✅ Login and receive JWT token
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# ✅ Return current user details
@app.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: schemas.UserOut = Depends(get_current_user)):
    return current_user

# ✅ Create a task (only for manager or admin)
@app.post("/tasks/", response_model=schemas.TaskOut)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    if current_user.role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not authorized to assign tasks.")
    return crud.create_task(db=db, task=task)

# ✅ Read tasks (admin/manager see all, employee sees only theirs)
@app.get("/tasks/", response_model=list[schemas.TaskOut])
def read_tasks(
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    if current_user.role in ["admin", "manager"]:
        return crud.get_all_tasks(db)
    return crud.get_tasks_by_user(db, user_id=current_user.id)

# ✅ Update a task
@app.put("/tasks/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: int,
    task_data: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    task = crud.update_task(db, task_id=task_id, task_data=task_data)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task

# ✅ Delete a task
@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.UserOut = Depends(get_current_user)
):
    task = crud.delete_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"message": "Task deleted successfully"}

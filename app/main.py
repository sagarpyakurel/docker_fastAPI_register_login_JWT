from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from database import Base, engine, SessionLocal
from models import Employee
import schemas
from auth import hash_password, verify_password
from jwt import create_access_token, SECRET_KEY, ALGORITHM

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Employee API is running"}

@app.post("/register")
def register(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        password=hash_password(employee.password)
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return {"message": "Employee registered", "id": new_employee.id}

@app.post("/login")
def login(employee: schemas.EmployeeLogin, db: Session = Depends(get_db)):
    user = db.query(Employee).filter(Employee.email == employee.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(employee.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.get("/profile")
def profile(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        return {"message": "Protected data", "email": email}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

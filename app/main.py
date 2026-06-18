from fastapi import FastAPI
from app.database import engine, Base

# Add DB Session Dependency
from sqlalchemy.orm import Session
from app.database import SessionLocal

# Create Register API
from fastapi import Depends
from app import schemas
from app.models import Employee

from app.auth import hash_password

from app.auth import verify_password
from app.schemas import EmployeeLogin
from app.jwt import create_access_token

from fastapi import HTTPException, Header
from app.jwt import jwt, SECRET_KEY, ALGORITHM
from jose import JWTError


app = FastAPI()

# This creates tables automatically in MySQL
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Employee API is running"}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/register")
def register(employee: schemas.EmployeeCreate,
             db: Session = Depends(get_db)):

    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        password=hash_password(employee.password)
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {
        "message": "Employee registered",
        "id": new_employee.id
    }



# @app.post("/login")
# def login(employee: EmployeeLogin, db: Session = Depends(get_db)):

#     user = db.query(Employee).filter(Employee.email == employee.email).first()

#     if not user:
#         return {"message": "User not found"}

#     if not verify_password(employee.password, user.password):
#         return {"message": "Incorrect password"}

#     return {
#         "message": "Login successful",
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email
#         }
#     }

@app.post("/login")
def login(employee: EmployeeLogin, db: Session = Depends(get_db)):

    user = db.query(Employee).filter(Employee.email == employee.email).first()

    if not user:
        return {"message": "User not found"}

    if not verify_password(employee.password, user.password):
        return {"message": "Incorrect password"}

    token = create_access_token({"sub": user.email})

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/profile")
def profile(authorization: str = Header(None)):
    print("AUTH HEADER:", authorization)

    if not authorization:
        raise HTTPException(status_code=401, detail="No token")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = parts[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        return {"message": "Protected data", "email": email}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

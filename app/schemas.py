from pydantic import BaseModel

class EmployeeCreate(BaseModel):
    name: str
    email: str
    password: str

class EmployeeLogin(BaseModel):
    email: str
    password: str
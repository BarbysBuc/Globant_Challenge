from pydantic import BaseModel
from datetime import datetime
from typing import List

class EmployeesPerQuarter(BaseModel):
    department: str
    job: str
    Q1: int
    Q2: int
    Q3: int
    Q4: int

class DepartmentsAboveMean(BaseModel):
    id: int
    department: str
    hired: int

class DepartmentCreate(BaseModel):
    id: int
    department: str

class JobCreate(BaseModel):
    id: int
    job: str

class EmployeeCreate(BaseModel):
    id: int
    name: str
    datetime: datetime
    department_id: int
    job_id: int
# Carga de la BBDD

import csv
from io import StringIO
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import Employee, Department, Job
from api.schemas import DepartmentCreate, JobCreate, EmployeeCreate
from fastapi import UploadFile

async def process_csv(file: UploadFile, db: AsyncSession):
    try:
        file_content = await file.read()  # Leer el contenido del archivo
        reader = csv.reader(StringIO(file_content.decode('utf-8')))
        file_name = file.filename.lower()
        if "departments" in file_name:
            await process_departments(reader, db)
        elif "jobs" in file_name:
            await process_jobs(reader, db)
        elif "hired_employees" in file_name:
            await process_hired_employees(reader, db)
        else:
            raise ValueError("El nombre del archivo no coincide con ninguna tabla")
    except Exception as e:
        raise Exception(f"Error al procesar el CSV: {e}")

async def process_departments(reader, db: AsyncSession):
    batch = []
    for row in reader:
        try:
            department_data = DepartmentCreate(id=int(row[0]), department=row[1])  # Validación con Pydantic
            department = Department(
                id=department_data.id,
                department=department_data.department
            )
            batch.append(department)
            if len(batch) >= 1000:
                await save_batch(db, batch)
                batch = []
        except Exception as e:
            raise Exception(f"Error en el registro {row}: {e}")
    if batch:
        await save_batch(db, batch)

async def process_jobs(reader, db: AsyncSession):
    batch = []
    for row in reader:
        try:
            job_data = JobCreate(id=int(row[0]), job=row[1])  # Validación con Pydantic
            job = Job(
                id=job_data.id,
                job=job_data.job
            )
            batch.append(job)
            if len(batch) >= 1000:
                await save_batch(db, batch)
                batch = []
        except Exception as e:
            raise Exception(f"Error pren el registro {row}: {e}")
    if batch:
        await save_batch(db, batch)

async def process_hired_employees(reader, db: AsyncSession):
    batch = []
    for row in reader:
        try:
            employee_data = EmployeeCreate(
                id=int(row[0]),
                name=row[1],
                datetime=row[2],
                department_id=int(row[3]),
                job_id=int(row[4])
            )  # Validación con Pydantic
            employee = Employee(
                id=employee_data.id,
                name=employee_data.name,
                datetime=employee_data.datetime,
                department_id=employee_data.department_id,
                job_id=employee_data.job_id
            )
            batch.append(employee)
            if len(batch) >= 1000:
                await save_batch(db, batch)
                batch = []
        except Exception as e:
            raise Exception(f"Error en el registro {row}: {e}")
    if batch:
        await save_batch(db, batch)

async def save_batch(db: AsyncSession, batch):
    async with db.begin():
        db.add_all(batch)
        await db.commit()
# Carga de la BBDD

import csv
from io import StringIO
from sqlalchemy.ext.asyncio import AsyncSession
from api.models import Employee, Department, Job

# Para manejar dinámicamente la tabla a cargar
async def process_csv(file, db: AsyncSession):
    reader = csv.reader(StringIO(file.read().decode('utf-8')))
    file_name = file.filename.lower()
    if "departments" in file_name:
        await process_departments(reader, db)
    elif "jobs" in file_name:
        await process_jobs(reader, db)
    elif "hired_employees" in file_name:
        await process_hired_employees(reader, db)
    else:
        raise ValueError("Invalid file name")

# Para cargar en batches
async def process_departments(reader, db: AsyncSession):
    batch = []
    async with db.begin():
        for row in reader:
            department = Department(
                id=row[0],
                department=row[1]
            )
            batch.append(department)
            if len(batch) >= 1000:
                await db.bulk_save_objects(batch)
                batch = []
        if batch:
            await db.bulk_save_objects(batch)

async def process_jobs(reader, db: AsyncSession):
    batch = []
    async with db.begin():
        for row in reader:
            job = Job(
                id=row[0],
                job=row[1]
            )
            batch.append(job)
            if len(batch) >= 1000:
                await db.bulk_save_objects(batch)
                batch = []
        if batch:
            await db.bulk_save_objects(batch)

async def process_hired_employees(reader, db: AsyncSession):
    batch = []
    async with db.begin():
        for row in reader:
            employee = Employee(
                id=row[0],
                name=row[1],
                datetime=row[2],
                department_id=row[3],
                job_id=row[4]
            )
            batch.append(employee)
            if len(batch) >= 1000:
                await db.bulk_save_objects(batch)
                batch = []
        if batch:
            await db.bulk_save_objects(batch)
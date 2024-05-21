# Load of DDBB

import csv
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from api.models import Employee, Department, Job
from api.schemas import DepartmentCreate, JobCreate, EmployeeCreate
import asyncio
import logging

logger = logging.getLogger(__name__)

async def process_csv(file: UploadFile, db: AsyncSession):
    try:
        content = await file.read()
        reader = csv.reader(StringIO(content.decode('utf-8')))
        file_name = file.filename.lower()
        if "departments" in file_name:
            await process_batch(reader, db, DepartmentCreate, Department, ["id", "department"])
        elif "jobs" in file_name:
            await process_batch(reader, db, JobCreate, Job, ["id", "job"])
        elif "hired_employees" in file_name:
            await process_batch(reader, db, EmployeeCreate, Employee, ["id", "name", "datetime", "department_id", "job_id"])
        else:
            raise ValueError("Invalid filename")
        logger.info(f"File {file.filename} succesfully processed")
    except Exception as e:
        logger.error(f"Failed when processing CSV {file.filename}: {e}")
        raise Exception(f"Failed when processing CSV: {e}")
    finally:
        await file.close()  # Close file

async def process_batch(reader: csv.reader, db: AsyncSession, schema, model, field_names):
    batch = []
    for row in reader:
        try:
            data = {key: value for key, value in zip(field_names, row)}
            # Data validation
            if all(data.values()):  # Ensure all values exists
                validated_data = schema(**data)  # Pydantic validation
                instance = model(**validated_data.dict())
                batch.append(instance)
            else:
                logger.warning(f"Row with failed data: {data}")
            if len(batch) >= 1000:
                await save_batch(db, batch)
                batch = []
        except Exception as e:
            logger.error(f"Error in the row {row}: {e}")
            raise Exception(f"Error in the row {row}: {e}")

    
    if batch:
        await save_batch(db, batch)

async def save_batch(db: AsyncSession, batch):
    for attempt in range(3):  # Retry until 3 times
        try:
            async with db.begin():  # Use begin to initiate transaction
                db.add_all(batch)
                await db.commit()
            logger.info("Batch succsesfully loaded")
            break
        except SQLAlchemyError as e:
            await db.rollback()  #Ensure transaction revert in error case
            if attempt == 2:
                logger.error(f"Failed to load batch after 3 attempts: {e}")
                raise Exception(f"Failed to load batch after 3 attempts: {e}")
            logger.warning(f"Re try, attempt: {attempt + 1}")
            await asyncio.sleep(1)  # Wait 1 sec before retry
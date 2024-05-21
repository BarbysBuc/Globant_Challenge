# Carga de la BBDD

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
            raise ValueError("El nombre del archivo no es válido")
        logger.info(f"Archivo {file.filename} procesado correctamente")
    except Exception as e:
        logger.error(f"Error al procesar el CSV {file.filename}: {e}")
        raise Exception(f"Error al procesar el CSV: {e}")
    finally:
        await file.close()  # Cerrar el archivo

async def process_batch(reader: csv.reader, db: AsyncSession, schema, model, field_names):
    batch = []
    for row in reader:
        try:
            data = {key: value for key, value in zip(field_names, row)}
            # Validar datos
            if all(data.values()):  # Asegúrate de que todos los valores existen
                validated_data = schema(**data)  # Validación con Pydantic
                instance = model(**validated_data.dict())
                batch.append(instance)
            else:
                logger.warning(f"Registro con valores faltantes: {data}")
            if len(batch) >= 1000:
                await save_batch(db, batch)
                batch = []
        except Exception as e:
            logger.error(f"Error en el registro {row}: {e}")
            raise Exception(f"Error en el registro {row}: {e}")

    
    if batch:
        await save_batch(db, batch)

async def save_batch(db: AsyncSession, batch):
    for attempt in range(3):  # Reintentar hasta 3 veces
        try:
            async with db.begin():  # Usar begin para iniciar una transacción
                db.add_all(batch)
                await db.commit()
            logger.info("Batch guardado correctamente")
            break
        except SQLAlchemyError as e:
            await db.rollback()  # Asegura que se revierta la transacción en caso de error
            if attempt == 2:
                logger.error(f"Error al guardar el batch después de 3 intentos: {e}")
                raise Exception(f"Error al guardar el batch después de 3 intentos: {e}")
            logger.warning(f"Reintentando guardar el batch, intento {attempt + 1}")
            await asyncio.sleep(1)  # Esperar 1 segundo antes de reintentar
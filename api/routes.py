#END POINTS AQUI

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from api.services import process_csv
from api.database import get_db
from api.schemas import EmployeesPerQuarter, DepartmentsAboveMean
from typing import List
import logging


router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/employees_per_quarter", response_model=List[EmployeesPerQuarter])
async def employees_per_quarter(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT 
                d.department,
                j.job,
                COALESCE(SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 1 THEN 1 ELSE 0 END),0) AS Q1,
                COALESCE(SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 2 THEN 1 ELSE 0 END),0) AS Q2,
                COALESCE(SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 3 THEN 1 ELSE 0 END),0) AS Q3,
                COALESCE(SUM(CASE WHEN EXTRACT(QUARTER FROM e.datetime) = 4 THEN 1 ELSE 0 END),0) AS Q4
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            JOIN jobs j ON e.job_id = j.id
            WHERE EXTRACT(YEAR FROM e.datetime) = 2021
            GROUP BY d.department, j.job
            ORDER BY d.department, j.job;
        """)
    
        result = await db.execute(query)
        rows = result.fetchall()
        if not rows:
            raise HTTPException(status_code=404, detail="No data found")
        logger.debug(f"Fetched rows: {rows}")
        response_data = [EmployeesPerQuarter(department=row[0], job=row[1], Q1=row[2], Q2=row[3], Q3=row[4], Q4=row[5]) for row in rows]
        logger.debug(f"Response data: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Error al obtener datos: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/departments_above_mean", response_model=List[DepartmentsAboveMean])
async def departments_above_mean(db: AsyncSession = Depends(get_db)):
    query = text("""
        WITH department_hires AS (
            SELECT 
                d.id,
                d.department,
                COUNT(e.id) AS hired
            FROM employees e
            JOIN departments d ON e.department_id = d.id
            WHERE EXTRACT(YEAR FROM e.datetime) = 2021
            GROUP BY d.id, d.department
        ),
        mean_hires AS (
            SELECT AVG(hired) AS mean_hired FROM department_hires
        )
        SELECT 
            dh.id,
            dh.department,
            dh.hired
        FROM department_hires dh
        JOIN mean_hires mh ON dh.hired > mh.mean_hired
        ORDER BY dh.hired DESC;
    """)
    
    result = await db.execute(query)
    return result.fetchall()

@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    logger.info(f"Recibido archivo: {file.filename}")
    if file.filename.endswith('.csv'):
        try:
            await process_csv(file, db)
            logger.info(f"Archivo {file.filename} procesado correctamente")
            return {"message": "Archivo cargado"}
        except Exception as e:
            logger.error(f"Error al procesar el archivo {file.filename}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Error al procesar el archivo: {str(e)}"
                )
    else:
        logger.warning(f"Formato de archivo no válido: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El formato del archivo debe ser .csv"
            )

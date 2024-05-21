#END POINTS AQUI

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.services import process_csv
from api.database import get_db
import logging


router = APIRouter()
logger = logging.getLogger(__name__)

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

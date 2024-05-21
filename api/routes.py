#END POINTS AQUI

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from api.services import process_csv

router = APIRouter()

async def get_db():
    from api.database import SessionLocal
    async with SessionLocal() as session:
        yield session

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if file.filename.endswith('.csv'):
        try:
            await process_csv(file, db)
            return {"message": "Archivo cargado"}
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El formato debe ser .csv")

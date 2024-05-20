#END POINTS AQUI

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.database import SessionLocal
from api.services import process_csv, batch_insert

router = APIRouter()

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    if file.filename.endswith('.csv'):
        await process_csv(file.file, db)
        return {"message": "Archivo cargado"}
    else:
        raise HTTPException(status_code=400, detail="El formato debe ser .csv")

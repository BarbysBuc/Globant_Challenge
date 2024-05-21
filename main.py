from fastapi import FastAPI
import logging
import api.database as db
from api.routes import router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

async def lifespan(app: FastAPI):
    # Este código se ejecuta al inicio
    await db.init_db()
    await db.check_tables()
    
    yield  # Aquí el control se cede a la aplicación

    # Este código se ejecuta al cierre
    logging.info("Aplicación cerrándose...")

app = FastAPI(lifespan=lifespan)

app.include_router(router)  # para incluir los endpoints
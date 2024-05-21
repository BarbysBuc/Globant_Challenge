# Conexión a la BBDD y creación de tablas

import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from api.models import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql+asyncpg://postgres:232172@localhost/g_challenge"

engine = create_async_engine(
    DATABASE_URL, 
    echo=True, # Motor con el registro de todas las sentencias SQL
    pool_timeout=120, # Aumenta el tiemeout
    pool_size=10,  # Tamaño del pool de conexiones
    max_overflow=20  # Máximo de conexiones adicionales que pueden ser creadas
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()  # Cerrar la sesión adecuadamente


# Inicializar la BBDD
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Verificar tablas
async def check_tables():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = result.fetchall()
        logger.info(f"Tablas en la base de datos: {tables}")
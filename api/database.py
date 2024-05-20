# Conexión a la BBDD y creación de tablas

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from api.models import Base

DATABASE_URL = "postgresql+asyncpg://postgres:232172@localhost/G_Challenge"

engine = create_async_engine(DATABASE_URL, echo=True) # Motor con el registro de todas las sentencias SQL 
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Inicializar la BBDD
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
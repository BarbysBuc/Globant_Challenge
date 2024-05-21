# DB Connection and table creations

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
    echo=True, # engine with all SQL sentences
    pool_timeout=120, # Increase timeout
    pool_size=10,  # size of connections
    max_overflow=20  # max of connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()  # Close session


# Initialize the DDBB
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Tables verification
async def check_tables():
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
        tables = result.fetchall()
        logger.info(f"Tablas en la base de datos: {tables}")
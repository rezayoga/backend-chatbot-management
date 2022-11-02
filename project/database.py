from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from project.config import settings

# https://fastapi.tiangolo.com/tutorial/sql-databases/#create-the-sqlalchemy-engine
engine = create_async_engine(
	settings.DATABASE_URL, connect_args=settings.DATABASE_CONNECT_DICT, echo=True
)
Base = declarative_base()


async def get_session() -> AsyncSession:
	async_session = sessionmaker(
		engine, class_=AsyncSession, expire_on_commit=False
	)
	async with async_session() as session:
		yield session

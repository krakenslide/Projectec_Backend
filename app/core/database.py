from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import DATABASE_URL, DB_SCHEMA

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"server_settings": {"search_path": f"{DB_SCHEMA},public"}},
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


#SYNC ENGINE SETUP
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg://",
    "postgresql+psycopg://",
)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=True,
    connect_args={
        "options": f"-csearch_path={DB_SCHEMA},public"
    },
)

SessionLocal = sessionmaker(
    bind=sync_engine,
    expire_on_commit=False,
)

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import DATABASE_URL, DB_SCHEMA

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"server_settings": {"search_path": f"{DB_SCHEMA},public"}},
)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

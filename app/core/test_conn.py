import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

DATABASE_URL = "postgresql+asyncpg://pmuser:Nagasiren99!@localhost:5432/pmtool"

async def test():
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.scalar())

    print("DB Connected!")

asyncio.run(test())
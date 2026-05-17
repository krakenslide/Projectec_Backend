import os
import re


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://pmuser:Nagasiren99!@localhost:5432/pmtool",
)

DB_SCHEMA = os.getenv("DB_SCHEMA", "app")

if not re.fullmatch(r"[a-z_][a-z0-9_]*", DB_SCHEMA):
    raise ValueError("DB_SCHEMA must be a lowercase PostgreSQL identifier")

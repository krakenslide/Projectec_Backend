# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import DB_SCHEMA
from app.core.database import engine
from app.models.base import Base
from app.modules.auth.models import User  
from app.modules.auth.v1.router import router as auth_router
from app.modules.projects.models import Project  
from app.modules.projects.v1.router import router as projects_router
from app.modules.issues.models import Issue
from app.modules.issues.v1.router import router as issues_router
from app.modules.organizations.models import Organization, OrganizationMember
from app.modules.organizations.v1.router import router as organizations_router
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SESSION_SECRET_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"'))
        # await conn.run_sync(Base.metadata.create_all)
    print("📦 Tables registered:", list(Base.metadata.tables.keys()))
    yield
    # teardown goes here (close pools, etc.)

app = FastAPI(title="Projectec", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(issues_router) 
app.include_router(organizations_router)

@app.get("/")
async def root():
    return {"status": "running"}



import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
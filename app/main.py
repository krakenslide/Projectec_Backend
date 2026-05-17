# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import DB_SCHEMA
from app.core.database import engine
from app.models.base import Base
from app.modules.auth.models import User  
from app.modules.auth.router import router as auth_router
from app.modules.projects.models import Project  
from app.modules.projects.router import router as projects_router
from app.modules.issues.models import Issue
from app.modules.issues.router import router as issues_router
from app.modules.organizations.models import Organization, OrganizationMember
from app.modules.organizations.router import router as organizations_router

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

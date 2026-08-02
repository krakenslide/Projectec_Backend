# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import DB_SCHEMA
from app.core.database import engine
from app.models.base import Base
from app.modules.auth.v1.router import router as auth_router
from app.models.user import User
from app.models.project import Project
from app.models.ticket import Ticket 
from app.models.organization import Organization
from app.modules.tickets.v1.router import router as ticket_router
from app.modules.users.v1.router import router as user_router
from app.modules.projects.v1.router import router as projects_router
from app.modules.organizations.v1.router import router as organizations_router
from app.modules.auth.v1.router import router as auth_router
from app.modules.comments.v1.router import router as comment_router
from starlette.middleware.sessions import SessionMiddleware
from app.modules.websockets.router import router as websocket_router

import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SESSION_SECRET_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"'))
    print("📦 Tables registered:", list(Base.metadata.tables.keys()))
    yield


app = FastAPI(title="Jiffy", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(organizations_router)
app.include_router(projects_router)
app.include_router(ticket_router)
app.include_router(comment_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"status": "running"}


import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

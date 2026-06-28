import bcrypt
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone
import os
import secrets
from app.models import User
from app.modules.mailer.service import send_verification_email

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def create_user(
    db: AsyncSession,
    email: str,
    password: str
):

    token = generate_verification_token()

    user = User(
        email=email,
        password_hash=hash_password(password),
        verification_token=token,
        is_verified=False,
    )

    db.add(user)

    await db.commit()

    await db.refresh(user)

    response = await send_verification_email(
        email,
        token
    )

    if not response["success"]:

        return {
            "success": False,
            "user": None,
            "error": response["error"]
        }

    return {
        "success": True,
        "user": user,
        "error": None
    }


def generate_verification_token():
    return secrets.token_urlsafe(32)
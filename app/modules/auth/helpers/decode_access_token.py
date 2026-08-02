from jose import JWTError, jwt
import os
# from app.core.config import settings
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

def decode_access_token(token: str) -> dict | None:
    try:
        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        return payload

    except JWTError:
        return None
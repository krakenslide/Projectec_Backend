from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from .schemas import RegisterRequest, LoginRequest, AuthResponse
from .service import create_user, get_user_by_email, verify_password, create_access_token
from .deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing_user = await get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = await create_user(db, request.email, request.password)
    token = create_access_token(data={"sub": str(user.id)})  # use id not email
    return AuthResponse(access_token=token)

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")  # 401 not 400
    
    token = create_access_token(data={"sub": str(user.id)})
    return AuthResponse(access_token=token)

@router.get("/me")
async def read_current_user(current_user = Depends(get_current_user)):
    return {"email": current_user.email, "id": current_user.id, "is_active": current_user.is_active}
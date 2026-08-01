from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.core.deps import get_db
from .schemas import RegisterRequest, LoginRequest, AuthResponse, RegisterResponse
from app.modules.auth.service import (
    create_user,
    get_user_by_email,
    verify_password,
    create_access_token,
)
from app.modules.auth.deps import get_current_user
from app.modules.mailer.service import is_valid_email
from fastapi import Request
from app.modules.auth.v1.google import oauth

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await is_valid_email(request.email) == False:
        return RegisterResponse(success=False, status_code=422, message="Invalid Email")

    existing_user = await get_user_by_email(db, request.email)
    if existing_user:
        return RegisterResponse(
            success=False, status_code=400, message="Email Already Registered"
        )

    response = await create_user(db, request.name, request.email, request.password)

    if response["success"] == False:
        return RegisterResponse(
            success=False,
            status_code=400,
            message=response["error"],
            data={"email": request.email},
        )

    # token = create_access_token(data={"sub": str(user.id)})  # use id not email
    return RegisterResponse(
        success=True,
        status_code=201,
        message="Verification Email Sent",
        data={"email": request.email, "id": response["user"].id},
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, request.email)

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401, detail="Invalid credentials"
        )  # 401 not 400
    if user.is_verified == False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email Has Not Been Verified",
        )

    token = create_access_token(data={"sub": str(user.id)})
    return AuthResponse(
        status_code=200, access_token=token, token_type="bearer", message="Token Issued"
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):

    return {"success": True, "message": f"{current_user.email} logged out successfully"}


@router.get("/me")
async def read_current_user(current_user=Depends(get_current_user)):
    return {
        "email": current_user.email,
        "name": current_user.name,
        "id": current_user.id,
        "is_active": current_user.is_active,
    }


@router.get("/verify-email")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.verification_token == token))

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )

    if user.is_verified:
        return {"success": True, "message": "Email already verified"}

    user.is_verified = True

    user.verification_token = None

    await db.commit()

    return {"success": True, "message": "Email verified successfully"}


@router.get("/google/login")
async def google_login(request: Request):

    redirect_uri = request.url_for("google_callback")
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback", name="google_callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):

    token = await oauth.google.authorize_access_token(request)

    user_info = token.get("userinfo")

    email = user_info["email"]

    result = await db.execute(select(User).where(User.email == email))

    user = result.scalar_one_or_none()

    if not user:

        user = User(
            email=email,
            is_verified=True,
        )

        db.add(user)

        await db.commit()

        await db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}

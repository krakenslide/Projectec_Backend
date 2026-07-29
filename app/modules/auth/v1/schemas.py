from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class AuthResponse(BaseModel):
    status_code: int
    access_token: str
    token_type: str = "bearer"
    message: str

class RegisterResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: Optional[dict] = None
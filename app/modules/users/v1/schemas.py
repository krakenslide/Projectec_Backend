from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from app.core.schemas import APIResponse
from app.models.user import User
from datetime import datetime


class UserListRequest(BaseModel):
    organization_id: UUID | None = None
    project_id: UUID | None = None
    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )
    page: int = Field(
        default=1,
        ge=1,
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
    )


class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(APIResponse[list[UserSchema]]):
    pass

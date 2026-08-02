from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommentCreateRequest(BaseModel):
    ticket_id: UUID
    description: str = Field(
        min_length=1,
        max_length=5000,
    )
    tagged_users: list[UUID] = Field(default_factory=list)


class CommentUpdateRequest(BaseModel):
    description: str = Field(
        min_length=1,
        max_length=5000,
    )


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_id: UUID

    description: str
    has_attachment: bool

    created_at: datetime | None
    updated_at: datetime | None

    created_by: UUID | None
    name: str | None
    email: str | None
    updated_by: UUID | None


class CommentListResponse(BaseModel):
    comments: list[CommentResponse]
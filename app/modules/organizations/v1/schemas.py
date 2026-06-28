from datetime import datetime
from typing import Literal
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

OrganizationRole = Literal["OWNER", "ADMIN", "MEMBER","VIEWER"]

# NOTE:
# SQLAlchemy models represent the database schema.
# They should not be used for request/response validation.
# Pydantic models are responsible for validating and serializing API data.
# Because Pydantic also:
# Parses JSON into Python objects.
# Performs type conversion (e.g., "123" → 123 if appropriate).
# Serializes Python objects back to JSON.
# Generates OpenAPI documentation in FastAPI.

class CreateOrganizationRequest(BaseModel):
    """
    Request schema for creating an organization.
    This model validates incoming data required to create a new organization.
    It represents the API contract and is independent of the database model.
    """
    name: str = Field(
        min_length=3,
        max_length=127,
        description="Organization name",
        examples=["Acme Corporation"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Organization description",
        examples=["Internal IT ticketing system"],
    )


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=127,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )

class OrganizationResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: str | None = None

class OrganizationMemberResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrganizationRole
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
class AddOrganizationMemberRequest(BaseModel):
    email: str
    role: OrganizationRole = "MEMBER"
    
class OrganizationMemberUserResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrganizationRole
    email: str
    created_at: datetime
    updated_at: datetime
    

#NOTE:
# The Architecture for your project is below
# HTTP Request
#      │
#      ▼
# Pydantic Request Schema
#      │
#      ▼
# Service
#      │
#      ▼
# SQLAlchemy Model
#      │
#      ▼
# Database
#      │
#      ▼
# SQLAlchemy Model
#      │
#      ▼
# Pydantic Response Schema
#      │
#      ▼
# HTTP Response
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

OrganizationRole = Literal["OWNER", "ADMIN", "MEMBER","VIEWER"]

class CreateOrganizationRequest(BaseModel):
    name: str
    
class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

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
    
    
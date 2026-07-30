from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, EmailStr

from app.core.schemas import APIResponse


from app.modules.organizations.rbac.roles import ProjectRole


class AddProjectMemberRequest(BaseModel):
    email: EmailStr
    role: ProjectRole = Field(default=ProjectRole.VIEWER, description="Project role")


class UpdateProjectMemberRoleRequest(BaseModel):
    role: ProjectRole


class ProjectMemberSchema(BaseModel):
    id: UUID
    project_id: UUID
    user_id: UUID
    email: EmailStr
    role: ProjectRole
    created_at: datetime
    updated_at: datetime


class ProjectMemberResponse(APIResponse[ProjectMemberSchema]):
    pass


class ProjectMemberListResponse(APIResponse[list[ProjectMemberSchema]]):
    pass


class CreateProjectRequest(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=127,
        description="Project name",
        examples=["Ticketing System"],
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Project description",
        examples=["Internal IT Ticketing System"],
    )

    code: str = Field(
        min_length=3,
        max_length=10,
    )


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=127,
    )

    description: Optional[str] = Field(
        default=None,
        max_length=500,
    )


class ProjectSchema(BaseModel):
    id: UUID
    organization_id: UUID
    name: str
    code: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectResponse(APIResponse[ProjectSchema]):
    pass


class ProjectListResponse(APIResponse[list[ProjectSchema]]):
    pass

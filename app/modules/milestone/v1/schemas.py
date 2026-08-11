from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class MilestoneSchema(BaseModel):
    id: UUID
    name: str


class ProjectMilestonesResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: list[MilestoneSchema]
    count: int


class MilestoneProgressPoint(BaseModel):
    date: datetime
    expected_percentage: float
    actual_percentage: float


class MilestoneProgressResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: list[MilestoneProgressPoint]
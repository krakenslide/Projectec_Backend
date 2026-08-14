from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class CreateMilestoneRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )


class MilestoneResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: MilestoneSchema


class MilestoneSchema(BaseModel):
    # TODO Why this model_config works?
    model_config = ConfigDict(from_attributes=True)

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


class ProjectMilestoneSummary(BaseModel):
    id: UUID
    name: str

    expected_start_date: datetime | None
    expected_end_date: datetime | None

    progress_percentage: float

    total_tickets: int
    completed_tickets: int


class ProjectMilestonesResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: list[ProjectMilestoneSummary]



class UserTicketStatusSummary(BaseModel):
    status: str
    count: int


class UserOrganizationTicketSummary(BaseModel):
    user_id: UUID
    organization_id: UUID

    total_tickets: int
    status_counts: list[UserTicketStatusSummary]


class UserOrganizationTicketSummaryResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: UserOrganizationTicketSummary
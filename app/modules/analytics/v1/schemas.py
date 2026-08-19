from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel
from datetime import date

class DeveloperCommentSummary(BaseModel):
    id: UUID
    description: str
    created_at: datetime

class DeveloperTicketSummary(BaseModel):
    project_name: str
    ticket_name: str
    status_changed: bool
    previous_status : str = ""
    current_status: str
    finished: bool
    hours_logged: int

    comments: list[DeveloperCommentSummary]


class DeveloperDailySummary(BaseModel):
    user_id: UUID
    developer_name: str
    organization_id: UUID

    report_start: datetime
    report_end: datetime

    tickets: list[DeveloperTicketSummary]

    total_tickets: int
    tickets_finished: int
    total_hours_logged: int
    total_comments: int


class DeveloperDailySummaryResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: DeveloperDailySummary



class EngagementTicketSchema(BaseModel):
    ticket_id: UUID
    ticket_key: str
    title: str

    # Dates actually used to render the Gantt bar
    start_date: date
    end_date: date

    # Original dates, useful for tooltips/details in frontend
    expected_start_date: date | None = None
    actual_start_date: date | None = None

    expected_end_date: date | None = None
    actual_end_date: date | None = None


class MemberEngagementSchema(BaseModel):
    member_id: UUID
    member_name: str
    tickets: list[EngagementTicketSchema]


class OrganizationEngagementGanttResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: list[MemberEngagementSchema]
    count: int
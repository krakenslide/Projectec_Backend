from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DeveloperTicketSummary(BaseModel):
    project_name: str
    ticket_name: str
    status_changed: bool
    current_status: str
    finished: bool
    hours_logged: int
    comments: list[str]


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
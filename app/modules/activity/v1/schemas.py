from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ActivitySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_id: UUID
    activity_type: str
    field_name: str | None
    old_value: str | None
    new_value: str | None
    created_at: datetime
    updated_at: datetime
    created_by: UUID | None
    updated_by: UUID | None


class TicketActivitiesResponse(BaseModel):
    success: bool
    status_code: int
    message: str
    data: list[ActivitySchema]
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.schemas import APIResponse
from app.modules.tickets.enum import (
    TicketPriority,
    TicketStatus,
    TicketType,
)


class CreateTicketRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=255,
    )

    description: Optional[str] = None

    type: TicketType

    priority: TicketPriority = TicketPriority.P2

    difficulty: int = Field(
        default=70,
        ge=1,
        le=100,
    )

    parent_ticket_id: Optional[UUID] = None

    assigned_to: Optional[UUID] = None

    expected_start_date: Optional[datetime] = None

    expected_end_date: Optional[datetime] = None

    actual_start_date: Optional[datetime] = None

    actual_end_date: Optional[datetime] = None

    reason_for_delay: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    hours_logged: float = Field(
        default=0,
        ge=0,
    )

    demo_link: Optional[str] = Field(
        default=None,
        max_length=500,
    )




class UpdateTicketRequest(BaseModel):
    title: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=255,
    )

    description: Optional[str] = None

    type: Optional[TicketType] = None

    priority: Optional[TicketPriority] = None

    status: Optional[TicketStatus] = None

    difficulty: Optional[int] = Field(
        default=None,
        ge=1,
        le=100,
    )

    parent_ticket_id: Optional[UUID] = None

    assigned_to: Optional[UUID] = None

    expected_start_date: Optional[datetime] = None

    expected_end_date: Optional[datetime] = None

    actual_start_date: Optional[datetime] = None

    actual_end_date: Optional[datetime] = None

    reason_for_delay: Optional[str] = Field(
        default=None,
        max_length=1000,
    )

    hours_logged: Optional[float] = Field(
        default=None,
        ge=0,
    )

    demo_link: Optional[str] = Field(
        default=None,
        max_length=500,
    )


class TicketSchema(BaseModel):
    id: UUID
    project_id: UUID
    organization_id: UUID
    parent_ticket_id: Optional[UUID]

    assigned_to: Optional[UUID]

    ticket_number: str

    title: str
    description: Optional[str]

    type: TicketType
    priority: TicketPriority
    status: TicketStatus

    difficulty: Optional[int]

    expected_start_date: Optional[datetime]
    expected_end_date: Optional[datetime]

    actual_start_date: Optional[datetime]
    actual_end_date: Optional[datetime]

    reason_for_delay: Optional[str]

    hours_logged: int

    demo_link: Optional[str]

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(APIResponse[TicketSchema]):
    pass


class TicketListResponse(APIResponse[list[TicketSchema]]):
    pass
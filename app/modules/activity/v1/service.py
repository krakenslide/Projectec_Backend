from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity import Activity
from app.models.ticket import Ticket

from .schemas import (
    ActivitySchema,
    TicketActivitiesResponse,
)


async def list_ticket_activities(
    db: AsyncSession,
    ticket_id: UUID,
) -> TicketActivitiesResponse:

    # Make sure ticket exists
    ticket = await db.scalar(
        select(Ticket).where(
            Ticket.id == ticket_id,
        )
    )

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    result = await db.scalars(
        select(Activity)
        .where(
            Activity.ticket_id == ticket_id,
        )
        .order_by(
            Activity.created_at.desc()
        )
    )

    activities = result.all()

    return TicketActivitiesResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Ticket activities retrieved successfully.",
        data=[
            ActivitySchema.model_validate(activity)
            for activity in activities
        ],
    )
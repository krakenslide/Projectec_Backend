from app.models.activity import Activity
from app.models.ticket import Ticket
from app.models.user import User
from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def create_activity_records(
    db: AsyncSession,
    ticket: Ticket,
    update_data: dict,
    current_user: User,
) -> None:
    activities: list[Activity] = []

    for field, new_value in update_data.items():

        old_value = getattr(ticket, field)

        if hasattr(old_value, "value"):
            old_value = old_value.value

        if hasattr(new_value, "value"):
            new_value = new_value.value

        if old_value == new_value:
            continue

        activities.append(
            Activity(
                ticket_id=ticket.id,
                user_id = current_user.id,
                action_type = "Value Update",
                field_name=f"{field}",
                old_value = old_value,
                new_value = new_value,
                created_by=current_user.id,
                updated_by=current_user.id,
            )
        )

    if activities:
        db.add_all(activities)
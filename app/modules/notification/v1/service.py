from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.models.ticket import Ticket
from app.models.user import User
from app.modules.notification.v1.enum import NotificationType

from .schemas import (
    NotificationCountResponse,
    NotificationListResponse,
    NotificationResponse,
    NotificationReadResponse,
    NotificationCreate
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.websockets.connection_manager import manager


async def list_notifications(
    db: AsyncSession,
    current_user_id: UUID,
) -> NotificationListResponse:

    result = await db.scalars(
        select(Notification)
        .where(Notification.recipient_user_id == current_user_id)
        .order_by(Notification.created_at.desc())
    )

    notifications = result.all()

    return NotificationListResponse(
        notifications=[
            NotificationResponse.model_validate(notification)
            for notification in notifications
        ]
    )


async def unread_notification_count(
    db: AsyncSession,
    current_user_id: UUID,
) -> NotificationCountResponse:

    unread_count = await db.scalar(
        select(func.count(Notification.id)).where(
            Notification.recipient_user_id == current_user_id,
            Notification.is_read.is_(False),
        )
    )

    return NotificationCountResponse(
        unread_count=unread_count or 0,
    )


async def mark_notification_read(
    db: AsyncSession,
    notification_id: UUID,
    current_user_id: UUID,
) -> NotificationReadResponse:

    await db.execute(
        update(Notification)
        .where(
            Notification.id == notification_id,
            Notification.recipient_user_id == current_user_id,
        )
        .values(
            is_read=True,
        )
    )

    await db.commit()

    return NotificationReadResponse(
        success=True,
    )


async def mark_all_notifications_read(
    db: AsyncSession,
    current_user_id: UUID,
) -> NotificationReadResponse:

    await db.execute(
        update(Notification)
        .where(
            Notification.recipient_user_id == current_user_id,
            Notification.is_read.is_(False),
        )
        .values(
            is_read=True,
        )
    )

    await db.commit()

    return NotificationReadResponse(
        success=True,
    )



async def create_notifications(
    db: AsyncSession,
    notifications: list[NotificationCreate],
) -> list[Notification]:

    notification_models: list[Notification] = []

    for data in notifications:

        notification = Notification(
            organization_id=data.organization_id,
            project_id=data.project_id,
            ticket_id=data.ticket_id,

            recipient_user_id=data.recipient_user_id,
            actor_user_id=data.actor_user_id,

            notification_type=data.notification_type,

            title=data.title,
            message=data.message,
            action_url=data.action_url,

            payload=data.payload,

            created_by=data.created_by,
        )

        notification_models.append(notification)

    db.add_all(notification_models)

    # Persist IDs without committing
    await db.flush()

    # Push realtime notifications
    for notification in notification_models:

        await manager.send_notification(
            user_id=str(notification.recipient_user_id),
            payload={
                "id": str(notification.id),
                "notification_type": notification.notification_type,
                "title": notification.title,
                "message": notification.message,
                "ticket_id": (
                    str(notification.ticket_id)
                    if notification.ticket_id
                    else None
                ),
                "project_id": (
                    str(notification.project_id)
                    if notification.project_id
                    else None
                ),
                "organization_id": str(notification.organization_id),
                "action_url": notification.action_url,
                "payload": notification.payload,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat()
                if notification.created_at
                else None,
            },
        )

    return notification_models



async def notify_ticket_assignment(
    db: AsyncSession,
    ticket: Ticket,
    assignee_id: UUID,
    actor: User,
):
    if assignee_id == actor.id:
        return

    await create_notifications(
        db=db,
        notifications=[
            NotificationCreate(
                organization_id=ticket.organization_id,
                project_id=ticket.project_id,
                ticket_id=ticket.id,

                recipient_user_id=assignee_id,
                actor_user_id=actor.id,

                notification_type=NotificationType.TICKET_ASSIGNED,

                title="Ticket Assigned",

                message=f"You have been assigned ticket {ticket.ticket_number}.",

                action_url=f"/projects/{ticket.project_id}/tickets/{ticket.id}",

                payload={
                    "ticket_number": ticket.ticket_number,
                    "ticket_title": ticket.title,
                },

                created_by=actor.id,
            )
        ],
    )

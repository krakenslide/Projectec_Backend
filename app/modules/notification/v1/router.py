from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.modules.auth.deps import get_current_user

from .schemas import (
    NotificationResponse,
    NotificationCountResponse,
)

from .service import (
    list_notifications,
    unread_notification_count,
    mark_notification_read,
    mark_all_notifications_read,
)


router = APIRouter(
    prefix="/v1/notifications",
    tags=["Notifications"],
)


@router.get("/", response_model=list[NotificationResponse])
async def list_all(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_notifications(
        db=db,
        current_user_id=current_user.id,
    )


@router.get("/unread-count", response_model=NotificationCountResponse)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await unread_notification_count(
        db=db,
        current_user_id=current_user.id,
    )


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await mark_notification_read(
        db=db,
        notification_id=notification_id,
        current_user_id=current_user.id,
    )


@router.patch("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await mark_all_notifications_read(
        db=db,
        current_user_id=current_user.id,
    )


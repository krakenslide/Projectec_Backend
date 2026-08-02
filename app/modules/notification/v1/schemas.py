from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from app.modules.notification.v1.enum import NotificationType

class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    project_id: UUID | None
    ticket_id: UUID | None
    recipient_user_id: UUID
    actor_user_id: UUID | None
    notification_type: str
    title: str
    message: str
    action_url: str | None
    payload: dict | None = None
    is_read: bool
    created_at: datetime | None


class NotificationListResponse(BaseModel):
    notifications: list[NotificationResponse]


class NotificationCountResponse(BaseModel):
    unread_count: int


class NotificationReadResponse(BaseModel):
    success: bool


class NotificationCreate(BaseModel):
    organization_id: UUID
    project_id: UUID | None
    ticket_id: UUID | None
    recipient_user_id: UUID
    actor_user_id: UUID | None
    notification_type: NotificationType
    title: str
    message: str
    action_url: str | None = None
    payload: dict | None = None
    created_by: UUID | None
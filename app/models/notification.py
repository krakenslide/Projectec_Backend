import uuid
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin

class Notification(Base, AuditMixin):
    __tablename__ = "notification"

    __table_args__ = (
        {"schema": DB_SCHEMA},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.organization.id"),
        nullable=False,
        index=True,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.project.id"),
        nullable=True,
        index=True,
    )

    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.ticket.id"),
        nullable=True,
        index=True,
    )

    recipient_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.user.id"),
        nullable=False,
        index=True,
    )

    actor_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.user.id"),
        nullable=True,
        index=True,
    )

    notification_type = Column(
        String(50),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    action_url = Column(
        String(500),
        nullable=True,
    )

    is_read = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        index=True,
    )

    payload = Column(JSONB, nullable=True)
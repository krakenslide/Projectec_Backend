import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class Activity(Base, AuditMixin):
    __tablename__ = "activity"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.ticket.id"),
        nullable=False,
        index=True,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.user.id"),
        nullable=False,
    )

    action_type = Column(
        String(50),
        nullable=False,
    )

    field_name = Column(
        String(50),
        nullable=True,
    )

    old_value = Column(
        Text,
        nullable=True,
    )

    new_value = Column(
        Text,
        nullable=True,
    )

    ticket = relationship(
        "Ticket",
        back_populates="activities",
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
    )
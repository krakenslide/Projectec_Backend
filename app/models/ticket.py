import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class Ticket(Base, AuditMixin):
    __tablename__ = "ticket"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.project.id"),
        nullable=False,
        index=True,
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.organization.id"),
        nullable=False,
        index=True,
    )

    parent_ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.ticket.id"),
        nullable=True,
        index=True,
    )

    assigned_to = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.user.id"),
        nullable=True,
        index=True,
    )

    milestone_id = Column(
            UUID(as_uuid=True),
            ForeignKey(f"{DB_SCHEMA}.milestone.id"),
            nullable=True,
            index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    priority = Column(
        String(20),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        index=True,
    )

    type = Column(
        String(30),
        nullable=False,
    )

    ticket_number = Column(
        String(30),
        nullable=False,
    )

    difficulty = Column(
        Integer,
        nullable=True,
    )

    expected_start_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    expected_end_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    actual_start_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    actual_end_date = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    reason_for_delay = Column(
        Text,
        nullable=True,
    )

    hours_logged = Column(
        Integer,
        default=0,
        nullable=False,
    )

    demo_link = Column(
        Text,
        nullable=True,
    )

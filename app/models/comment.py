import uuid

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Comment(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "comment"
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

    description = Column(
        Text,
        nullable=False,
    )

    has_attachment = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ticket = relationship(
    #     "Ticket",
    #     back_populates="comments",
    # )

    # attachments = relationship(
    #     "Attachment",
    #     back_populates="comment",
    #     cascade="all, delete-orphan",
    # )

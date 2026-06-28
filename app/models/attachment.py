import uuid

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class Attachment(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "attachment"

    __table_args__ = (
        CheckConstraint(
            """
            (
                ticket_id IS NOT NULL AND comment_id IS NULL
            )
            OR
            (
                ticket_id IS NULL AND comment_id IS NOT NULL
            )
            """,
            name="ck_attachment_parent",
        ),
        {"schema": DB_SCHEMA},
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    ticket_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.ticket.id"),
        nullable=True,
        index=True,
    )

    comment_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.comment.id"),
        nullable=True,
        index=True,
    )

    original_file_name = Column(
        String(255),
        nullable=False,
    )

    stored_file_name = Column(
        String(255),
        nullable=False,
    )

    mime_type = Column(
        String(100),
        nullable=False,
    )

    file_size = Column(
        Integer,
        nullable=False,
    )

    storage_path = Column(
        Text,
        nullable=False,
    )

    uploaded_by = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.user.id"),
        nullable=False,
    )

    ticket = relationship(
        "Ticket",
        back_populates="attachments",
    )

    comment = relationship(
        "Comment",
        back_populates="attachments",
    )

    uploader = relationship(
        "User",
        foreign_keys=[uploaded_by],
    )
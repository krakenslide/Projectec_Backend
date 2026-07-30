from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql import func

from app.core.config import DB_SCHEMA


class AuditMixin:
    """
    Adds audit columns to a model.
    """

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @declared_attr
    def created_by(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey(f"{DB_SCHEMA}.user.id"),
            nullable=True,
        )

    @declared_attr
    def updated_by(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey(f"{DB_SCHEMA}.user.id"),
            nullable=True,
        )


class SoftDeleteMixin:
    """
    Adds soft delete columns to a model.
    """

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    @declared_attr
    def deleted_by(cls):
        return Column(
            UUID(as_uuid=True),
            ForeignKey(f"{DB_SCHEMA}.user.id"),
            nullable=True,
        )

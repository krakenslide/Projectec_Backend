import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class Milestone(Base, AuditMixin):
    __tablename__ = "milestone"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.project.id"),
        nullable=False,
        index=True,
    )
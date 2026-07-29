import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class UserProject(Base, AuditMixin):
    __tablename__ = "user_project"
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

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.user.id"),
        nullable=False,
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.role.id"),
        nullable=False,
    )

    __table_args__ = (
    UniqueConstraint(
        "project_id",
        "user_id",
        name="uq_project_user",
    ),
    {"schema": DB_SCHEMA},
)
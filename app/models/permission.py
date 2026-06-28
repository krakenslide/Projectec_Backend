import uuid

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class Permission(Base, AuditMixin):
    __tablename__ = "permission"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(100),
        unique=True,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    roles = relationship(
        "RolePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )
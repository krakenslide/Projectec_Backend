import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class Organization(Base, AuditMixin):
    __tablename__ = "organization"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(127),
        unique=True,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    # users = relationship(
    #     "UserOrganization",
    #     back_populates="organization",
    #     cascade="all, delete-orphan",
    # )

    # projects = relationship(
    #     "Project",
    #     back_populates="organization",
    #     cascade="all, delete-orphan",
    # )

    # roles = relationship(
    #     "Role",
    #     back_populates="organization",
    #     foreign_keys="Role.organization_id",
    #     cascade="all, delete-orphan",
    # )

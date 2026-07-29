import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class Project(Base, AuditMixin):
    __tablename__ = "project"
    __table_args__ = {"schema": DB_SCHEMA}

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

    name = Column(
        String(127),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )
    code = Column(
        String(10),
        nullable=False,
    )

    __table_args__ = (
    UniqueConstraint(
        "organization_id",
        "name",
        name="uq_project_organization_name",
    ),
    {"schema": DB_SCHEMA},
)

    # organization = relationship(
    #     "Organization",
    #     back_populates="projects",
    # )

    # tickets = relationship(
    #     "Ticket",
    #     back_populates="project",
    #     cascade="all, delete-orphan",
    # )
import uuid

from sqlalchemy import (
    Column,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class UserOrganization(Base, AuditMixin):
    __tablename__ = "user_organization"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "organization_id",
            name="uq_user_organization",
        ),
        {
            "schema": DB_SCHEMA,
        },
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.user.id"),
        nullable=False,
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.organization.id"),
        nullable=False,
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.role.id"),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="organizations",
        foreign_keys=[user_id],
    )

    organization = relationship(
        "Organization",
        back_populates="users",
        foreign_keys=[organization_id],
    )

    role = relationship(
        "Role",
        back_populates="users",
        foreign_keys=[role_id],
    )
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin, SoftDeleteMixin


class User(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "user"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(127),
        nullable=True,
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False,
    )

    password_hash = Column(
        String,
        nullable=True,
    )

    phone_number = Column(
        String(15),
        nullable=True,
    )

    nationality = Column(
        String(31),
        nullable=True,
    )

    verification_token = Column(
        String(255),
        nullable=True,
    )

    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    two_factor_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    organizations = relationship(
        "UserOrganization",
        back_populates="user",
        foreign_keys="UserOrganization.user_id",
        )
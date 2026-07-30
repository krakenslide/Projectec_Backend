import uuid

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class RolePermission(Base, AuditMixin):
    __tablename__ = "role_permission"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.role.id"),
        nullable=False,
    )

    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.permission.id"),
        nullable=False,
    )

    # role = relationship(
    #     "Role",
    #     back_populates="permissions",
    # )

    # permission = relationship(
    #     "Permission",
    #     back_populates="roles",
    # )

import uuid

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.config import DB_SCHEMA
from app.models.base import Base
from app.models.mixins import AuditMixin


class Role(Base, AuditMixin):
    __tablename__ = "role"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String(50),
        unique=True,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    permissions = relationship(
        "RolePermission",
        back_populates="role",
        cascade="all, delete-orphan",
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.organization.id"),
        nullable=False,
    )

    organization = relationship(
        "Organization",
        back_populates="roles",
        foreign_keys=[organization_id],
    )

    users = relationship(
        "UserOrganization",
        back_populates="role",
    )


# NOTE
# organization_id is for the database.
# organization is for Python. "Whenever someone accesses role.organization, automatically fetch the Organization object using organization_id."

# Example
# Suppose the database contains:

# Organization Table
# id	name
# 10	Acme

# Role Table
# id	name	organization_id
# 5	    Owner	10

# Without relationship()
# You only have:
# role.organization_id

# Output:
# UUID("10...")

# If you want the organization name:
# organization = await db.get(
#     Organization,
#     role.organization_id
# )

# You have to write another query yourself.

# With relationship()

# Now you can simply do:

# role.organization.name

# SQLAlchemy automatically executes the join.

# It's equivalent to:
# SELECT *
# FROM role
# JOIN organization
# ON role.organization_id = organization.id;
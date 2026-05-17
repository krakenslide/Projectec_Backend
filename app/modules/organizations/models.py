import uuid

from sqlalchemy import Column, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.core.config import DB_SCHEMA

class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {"schema": DB_SCHEMA}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False, unique=True)
    
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id"),
        nullable=False
    )
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
class OrganizationMember(Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_user"),
        {"schema": DB_SCHEMA}
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.organizations.id"),
        nullable=False
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id"),
        nullable=False
    )
    
    role = Column(String, default="MEMBER", nullable=False) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
import uuid 
from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.core.config import DB_SCHEMA

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.users.id"),  
        nullable=False
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(f"{DB_SCHEMA}.organizations.id"),  
        nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    owner = relationship("User", back_populates="projects")

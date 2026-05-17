import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.core.config import DB_SCHEMA

class Issue(Base):
    __tablename__ = 'issues'
    __table_args__ = {'schema': DB_SCHEMA}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    status = Column(String, default="TODO", nullable=False)
    priority = Column(String, default="MEDIUM", nullable=False)
    position = Column(Integer, nullable=False, default = 0)  # For ordering issues within a project
    
    project_id = Column(UUID(as_uuid=True), ForeignKey(f'{DB_SCHEMA}.projects.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    project = relationship("Project")
    
    
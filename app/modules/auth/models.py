from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship  
import uuid

from app.models.base import Base
from app.core.config import DB_SCHEMA

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": DB_SCHEMA}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    verification_token = Column(String, nullable = False)
    is_verified = Column(Boolean, default=False, nullable=True)
    projects = relationship("Project", back_populates="owner")
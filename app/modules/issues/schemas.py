from pydantic import BaseModel
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class CreateIssueRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = "MEDIUM"
    project_id: UUID

class UpdateIssueStatusRequest(BaseModel):
    status: Literal["TODO", "IN_PROGRESS", "DONE"]

    
class IssueResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    status: str
    priority: Literal["LOW", "MEDIUM", "HIGH"]
    position: int
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class UpdateIssueRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Literal["LOW", "MEDIUM", "HIGH"]] = None
    
class MoveIssueRequest(BaseModel):
    status: Literal["TODO", "IN_PROGRESS", "DONE"]
    position: int
    

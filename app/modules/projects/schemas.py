from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    
class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    owner_id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class BoardIssueResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    position: int
    project_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        
class BoardResponse(BaseModel):
    TODO: List[BoardIssueResponse]
    IN_PROGRESS: List[BoardIssueResponse]
    DONE: List[BoardIssueResponse]
    
class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    
class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    organization_id: UUID
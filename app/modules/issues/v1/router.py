from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.deps import get_db
from app.modules.auth.deps import get_current_user

from .schemas import CreateIssueRequest, IssueResponse, UpdateIssueStatusRequest, UpdateIssueRequest, MoveIssueRequest
from ..service import create_issue, get_issues_by_project, update_issue_status, delete_issue, update_issue, move_issue

router = APIRouter(prefix="/v1/issues", tags=["Issues"])

@router.post("/", response_model=IssueResponse)
async def create(data: CreateIssueRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await create_issue(db, data, current_user.id)

@router.get("/{project_id}", response_model=list[IssueResponse])
async def list_issues_by_project(project_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await get_issues_by_project(db, project_id, current_user.id)

@router.patch("/{issue_id}/status", response_model=IssueResponse)
async def update_status(issue_id: UUID, data: UpdateIssueStatusRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await update_issue_status(db = db, issue_id = issue_id, status = data.status, user_id=current_user.id)

@router.patch("/{issue_id}/move", response_model=IssueResponse)
async def move(issue_id: UUID, data: MoveIssueRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await move_issue(db = db, issue_id = issue_id, status = data.status, position = data.position, user_id=current_user.id)

@router.patch("/{issue_id}", response_model=IssueResponse)
async def update(issue_id: UUID, data: UpdateIssueRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await update_issue(db = db, issue_id = issue_id, data = data, user_id=current_user.id)
    
@router.delete("/{issue_id}")
async def remove(issue_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await delete_issue(db, issue_id, current_user.id)


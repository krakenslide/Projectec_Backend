from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.user import User
from app.modules.auth.deps import get_current_user

from .schemas import (
    CreateMilestoneRequest,
    MilestoneProgressResponse,
    MilestoneResponse,
    ProjectMilestonesResponse,
)

from .service import (
    create_milestone,
    get_milestone_progress,
    list_project_milestones,
)


router = APIRouter(
    prefix="/v1/milestones",
    tags=["Milestones"],
)


@router.post(
    "/projects/{project_id}",
    response_model=MilestoneResponse,
    status_code=201,
)
async def create_milestone_endpoint(
    project_id: UUID,
    data: CreateMilestoneRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_milestone(
        db=db,
        project_id=project_id,
        data=data,
        current_user=current_user,
    )

@router.get(
    "/projects/{project_id}",
    response_model=ProjectMilestonesResponse,
)
async def list_project_milestones_endpoint(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_project_milestones(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )


@router.get(
    "/projects/{project_id}/{milestone_name}/progress",
    response_model=MilestoneProgressResponse,
)
async def get_milestone_progress_endpoint(
    project_id: UUID,
    milestone_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_milestone_progress(
        db=db,
        project_id=project_id,
        milestone_name=milestone_name,
        current_user=current_user,
    )
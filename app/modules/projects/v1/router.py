from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.modules.auth.deps import get_current_user

from .schemas import (
    CreateProjectRequest,
    ProjectResponse,
    BoardResponse,
    UpdateProjectRequest,
)

from ..service import (
    create_project,
    get_projects_by_user,
    get_project_board,
    get_project_by_id,
    update_project as update_project_service,
    delete_project,
)


router = APIRouter(prefix="/v1/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse)
async def create_new_project(
    request: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await create_project(
        db=db,
        name=request.name,
        description=request.description,
        owner_id=current_user.id,
        organization_id=request.organization_id,
    )


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_projects_by_user(db, current_user.id)


@router.get("/{project_id}/board", response_model=BoardResponse)
async def get_board(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_project_board(db, project_id, current_user.id)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_project_by_id(db, project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project_route(
    project_id: UUID,
    data: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await update_project_service(
        db=db,
        project_id=project_id,
        data=data,
        user_id=current_user.id,
    )


@router.delete("/{project_id}")
async def remove_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await delete_project(db, project_id, current_user.id)
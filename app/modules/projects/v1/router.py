from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.modules.auth.deps import get_current_user
from app.modules.projects.v1.schemas import (
    CreateProjectRequest,
    UpdateProjectRequest,
    ProjectResponse,
    ProjectListResponse,
    ProjectMemberResponse,
    AddProjectMemberRequest,
    ProjectMemberListResponse,
    UpdateProjectMemberRoleRequest,
)

from app.core.schemas import APIResponse

from .service import (
    create_project,
    get_projects_for_organization,
    get_project,
    update_project,
    delete_project,
    add_project_member,
    list_project_members,
    update_project_member_role,
    remove_project_member
)

router = APIRouter(
    prefix="/v1/projects",
    tags=["Project"],
)


@router.post(
    "/organizations/{organization_id}",
    response_model=ProjectResponse,
)
async def create(
    organization_id: UUID,
    data: CreateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await create_project(
        db=db,
        organization_id=organization_id,
        data=data,
        current_user_id=current_user.id,
    )


@router.get(
    "/organizations/{organization_id}",
    response_model=ProjectListResponse,
)
async def list_projects(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_projects_for_organization(
        db=db,
        organization_id=organization_id,
        current_user_id=current_user.id,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def get(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await get_project(
        db=db,
        project_id=project_id,
        current_user_id=current_user.id,
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update(
    project_id: UUID,
    data: UpdateProjectRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await update_project(
        db=db,
        project_id=project_id,
        data=data,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def delete(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await delete_project(
        db=db,
        project_id=project_id,
        current_user_id=current_user.id,
    )



@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
)
async def add_member(
    project_id: UUID,
    data: AddProjectMemberRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await add_project_member(
        db=db,
        project_id=project_id,
        data=data,
        current_user_id=current_user.id,
    )


@router.get(
    "/{project_id}/members",
    response_model=ProjectMemberListResponse,
)
async def list_members(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await list_project_members(
        db=db,
        project_id=project_id,
        current_user_id=current_user.id,
    )


@router.patch(
    "/{project_id}/members/{user_id}",
    response_model=ProjectMemberResponse,
)
async def update_member_role(
    project_id: UUID,
    user_id: UUID,
    data: UpdateProjectMemberRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await update_project_member_role(
        db=db,
        project_id=project_id,
        user_id=user_id,
        data=data,
        current_user_id=current_user.id,
    )


@router.delete(
    "/{project_id}/members/{user_id}",
    response_model=APIResponse[None],
)
async def remove_member(
    project_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await remove_project_member(
        db=db,
        project_id=project_id,
        user_id=user_id,
        current_user_id=current_user.id,
    )
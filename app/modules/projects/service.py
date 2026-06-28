from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Project
from app.models import Ticket as Issue
from app.models import Organization as OrganizationMember


async def ensure_user_in_organization(db: AsyncSession, organization_id, user_id):
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == organization_id)
        .where(OrganizationMember.user_id == user_id)
    )

    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(status_code=403, detail="Not allowed")

    return membership


async def create_project(
    db: AsyncSession,
    name: str,
    description: str | None,
    owner_id,
    organization_id,
) -> Project:
    await ensure_user_in_organization(db, organization_id, owner_id)

    project = Project(
        name=name,
        description=description,
        owner_id=owner_id,
        organization_id=organization_id,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    return project


async def get_projects_by_user(db: AsyncSession, user_id) -> list[Project]:
    result = await db.execute(
        select(Project)
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Project.organization_id,
        )
        .where(OrganizationMember.user_id == user_id)
        .order_by(Project.created_at.desc())
    )

    return result.scalars().all()


async def get_project_for_user(db: AsyncSession, project_id, user_id) -> Project:
    result = await db.execute(
        select(Project)
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Project.organization_id,
        )
        .where(Project.id == project_id)
        .where(OrganizationMember.user_id == user_id)
    )

    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


async def get_project_by_id(db: AsyncSession, project_id, user_id) -> Project:
    return await get_project_for_user(db, project_id, user_id)


async def get_project_board(db: AsyncSession, project_id, user_id):
    await get_project_for_user(db, project_id, user_id)

    result = await db.execute(
        select(Issue)
        .where(Issue.project_id == project_id)
        .order_by(Issue.status.asc(), Issue.position.asc(), Issue.created_at.asc())
    )

    issues = result.scalars().all()

    board = {
        "TODO": [],
        "IN_PROGRESS": [],
        "DONE": [],
    }

    for issue in issues:
        if issue.status in board:
            board[issue.status].append(issue)

    return board


async def update_project(db: AsyncSession, project_id, data, user_id) -> Project:
    project = await get_project_for_user(db, project_id, user_id)

    if data.name is not None:
        project.name = data.name

    if data.description is not None:
        project.description = data.description

    await db.commit()
    await db.refresh(project)

    return project


async def delete_project(db: AsyncSession, project_id, user_id):
    project = await get_project_for_user(db, project_id, user_id)

    await db.delete(project)
    await db.commit()

    return {"message": "Project deleted"}
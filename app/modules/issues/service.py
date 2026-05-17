from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .models import Issue
from app.modules.projects.models import Project 

async def create_issue(db: AsyncSession, data, user_id):
    project_result = await db.execute(
        select(Project).where(Project.id == data.project_id)
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    position_result = await db.execute(
        select(func.coalesce(func.max(Issue.position), 0))
        .where(Issue.project_id == data.project_id)
        .where(Issue.status == "TODO")
    )

    next_position = position_result.scalar_one() + 1000

    issue = Issue(
        title=data.title,
        description=data.description,
        priority=data.priority,
        project_id=data.project_id,
        position=next_position,
    )

    db.add(issue)
    await db.commit()
    await db.refresh(issue)

    return issue


async def get_issues_by_project(db: AsyncSession, project_id, user_id):
    project_result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    result = await db.execute(
        select(Issue).where(Issue.project_id == project_id)
    )

    return result.scalars().all()

async def update_issue_status(db: AsyncSession, issue_id, status: str, user_id):
    issue = await get_issue_with_project_access(db, issue_id, user_id)

    issue.status = status

    await db.commit()
    await db.refresh(issue)

    return issue

async def get_issue_with_project_access(db: AsyncSession, issue_id, user_id): 
    result = await db.execute(
        select(Issue).where(Issue.id == issue_id)
    )
    issue = result.scalar_one_or_none()
    
    if not issue: 
        raise HTTPException(status_code=404, detail="Issue not found")
    
    project_result = await db.execute(
        select(Project).where(Project.id == issue.project_id)
    )
    
    project = project_result.scalar_one_or_none()
    
    if not project: 
        raise HTTPException(status_code=404, detail="Project not found")    
    
    if project.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    return issue


async def update_issue(db: AsyncSession, issue_id, data, user_id):
    issue = await get_issue_with_project_access(db, issue_id, user_id)
    
    if data.title is not None:
        issue.title = data.title
    if data.description is not None:
        issue.description = data.description
    if data.priority is not None:
        issue.priority = data.priority
        
    await db.commit()
    await db.refresh(issue)
    
    return issue

async def delete_issue(db: AsyncSession, issue_id, user_id):
    issue = await get_issue_with_project_access(db, issue_id, user_id)
    
    await db.delete(issue)
    await db.commit()
    
    return {"detail": "Issue deleted"}

async def move_issue(db: AsyncSession, issue_id, status: str, position: int, user_id):
    issue = await get_issue_with_project_access(db, issue_id, user_id)
    
    issue.status = status
    issue.position = position
    
    await db.commit()
    await db.refresh(issue)
    
    return issue
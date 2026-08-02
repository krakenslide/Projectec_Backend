from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.models import Project
from app.modules.issues.models import Issue
from app.modules.organizations.models import OrganizationMember

async def get_dashboard_summary(db: AsyncSession, user_id):
    accessible_projects_subquery = (
        select(Project.id)
        .join(OrganizationMember, OrganizationMember.organization_id == Project.organization_id)
        .where(OrganizationMember.user_id == user_id)
        .subquery()
    )
    
    total_projects_result = await db.execute(
        select(func.count()).select_from(accessible_projects_subquery)
    )
    
    total_projects = total_projects_result.scalar() or 0
    
    total_issue_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.project_id.in_(select(accessible_projects_subquery.c.id)))
    )
    
    total_issues = total_issue_result.scalar() or 0
    
    todo_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.project_id.in_(select(accessible_projects_subquery.c.id)))
        .where(Issue.status == "TODO")
    )
    
    todo_count = todo_result.scalar() or 0
    
    in_progress_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.project_id.in_(select(accessible_projects_subquery.c.id)))
        .where(Issue.status == "IN_PROGRESS")
    )
    
    in_progress_count = in_progress_result.scalar() or 0
    
    done_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.project_id.in_(select(accessible_projects_subquery.c.id)))
        .where(Issue.status == "DONE")
    )
    
    done_count = done_result.scalar() or 0
    
    high_priority_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.project_id.in_(select(accessible_projects_subquery.c.id)))
        .where(Issue.priority == "HIGH")
    )
    
    high_priority_count = high_priority_result.scalar() or 0
    
    my_assigned_result = await db.execute(
        select(func.count(Issue.id))
        .where(Issue.project_id.in_(select(accessible_projects_subquery.c.id)))
        .where(Issue.assignee_id == user_id)
    )
    
    my_assigned_count = my_assigned_result.scalar() or 0
    
    return {
        "total_projects": total_projects,
        "total_issues": total_issues,
        "todo_count": todo_count,
        "in_progress_count": in_progress_count,
        "done_count": done_count,
        "high_priority_count": high_priority_count,
        "my_assigned_count": my_assigned_count
    }
    
async def get_my_assigned_issues(db: AsyncSession, user_id):
    result = await db.execute(
        select(Issue)
        .join(Project, Project.id == Issue.project_id)
        .join(OrganizationMember, OrganizationMember.organization_id == Project.organization_id)
        .where(OrganizationMember.user_id == user_id)
        .where(Issue.assignee_id == user_id)
        .order_by(Issue.created_at.desc())
    )
    
    return result.scalars().all()

async def get_recent_issues(db: AsyncSession, user_id, limit: int = 10):
    result = await db.execute(
        select(Issue)
        .join(Project, Project.id == Issue.project_id)
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Project.organization_id,
        )
        .where(OrganizationMember.user_id == user_id)
        .order_by(Issue.updated_at.desc(), Issue.created_at.desc())
        .limit(limit)
    )

    return result.scalars().all()
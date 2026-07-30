from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.user_project import UserProject
from fastapi import HTTPException, status
from app.modules.organizations.rbac.roles import ProjectRole
from app.models.ticket import Ticket
from app.models.user import User
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.permission import Permission


from sqlalchemy import desc, select


async def validate_project_membership(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
) -> tuple[Project, UserProject]:
    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    membership = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not a member of this project.",
        )

    # Query 1
    role = await db.scalar(select(Role).where(Role.id == membership.role_id))

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Project role configuration is invalid.",
        )

    # Query 2
    permission_ids = await db.scalars(
        select(RolePermission.permission_id).where(RolePermission.role_id == role.id)
    )

    # Query 3
    permissions = await db.scalars(
        select(Permission.name).where(Permission.id.in_(permission_ids.all()))
    )

    return project, membership, role, set(permissions.all())


def validate_project_role(
    role,
    allowed_roles: list[ProjectRole],
) -> None:
    print("ROLE: ", role.name)
    print("ALLOWED ROLES: ", allowed_roles)
    if role.name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )


async def validate_ticket(
    db: AsyncSession,
    ticket_id: UUID,
) -> Ticket:
    """
    Validates that the ticket exists.

    Returns:
        Ticket

    Raises:
        HTTPException(404): If the ticket does not exist.
    """

    ticket = await db.scalar(select(Ticket).where(Ticket.id == ticket_id))

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found.",
        )

    return ticket


async def validate_ticket_assignee(
    db: AsyncSession,
    project_id: UUID,
    user_id: UUID,
) -> User:
    """
    Validates that:
    1. The user exists.
    2. The user is a member of the project.

    Returns:
        User

    Raises:
        HTTPException(404): If the user does not exist.
        HTTPException(400): If the user is not a member of the project.
    """

    user = await db.scalar(select(User).where(User.id == user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found.",
        )

    membership = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user is not a member of this project.",
        )

    return user


async def validate_parent_ticket(
    db: AsyncSession,
    parent_ticket_id: UUID,
    project_id: UUID,
    current_ticket_id: UUID | None = None,
) -> Ticket:
    """
    Validates that:
    1. Parent ticket exists.
    2. Parent ticket belongs to the same project.
    3. Ticket cannot be its own parent.

    Returns:
        Ticket

    Raises:
        HTTPException(404): Parent ticket not found.
        HTTPException(400): Invalid parent ticket.
    """

    parent_ticket = await db.scalar(select(Ticket).where(Ticket.id == parent_ticket_id))

    if parent_ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parent ticket not found.",
        )

    if parent_ticket.project_id != project_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parent ticket belongs to another project.",
        )

    if current_ticket_id is not None and parent_ticket.id == current_ticket_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A ticket cannot be its own parent.",
        )

    return parent_ticket


async def _generate_ticket_number(
    db: AsyncSession,
    project: Project,
) -> str:
    """
    Generates the next ticket number for a project.

    Example:
        AUTH-001
        AUTH-002
        AUTH-003
    """

    latest_ticket = await db.scalar(
        select(Ticket)
        .where(Ticket.project_id == project.id)
        .order_by(desc(Ticket.created_at))
        .limit(1)
    )

    if latest_ticket is None:
        next_number = 1
    else:
        try:
            next_number = int(latest_ticket.ticket_number.split("-")[-1]) + 1
        except (ValueError, IndexError):
            next_number = 1

    return f"{project.code}-{next_number:03d}"

from fastapi import HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ticket import Ticket
from app.models.project import Project
from app.modules.mailer.notifications import send_email_notification
from app.modules.tickets.helpers.helpers import (
    validate_project_membership,
    validate_parent_ticket,
    validate_ticket,
    validate_project_role,
    validate_ticket_assignee,
    _generate_ticket_number,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.modules.organizations.rbac.roles import ProjectRole
from app.models.ticket import Ticket
from app.modules.tickets.enum import TicketStatus
from app.modules.tickets.v1.schemas import (
    CreateTicketRequest,
    TicketListResponse,
    TicketSchema,
    TicketResponse,
    UpdateTicketRequest,
    APIResponse,
)


@staticmethod
async def create_project_ticket(
    db: AsyncSession,
    project_id: UUID,
    request: CreateTicketRequest,
    current_user: User,
) -> TicketResponse:
    project, membership, role, permissions = await validate_project_membership(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    validate_project_role(
        role=role,
        allowed_roles=[
            ProjectRole.PROJECT_OWNER,
            ProjectRole.PROJECT_ADMIN,
            ProjectRole.ENGINEER,
            ProjectRole.QA,
            ProjectRole.REPORTER,
        ],
    )

    if request.parent_ticket_id:
        await validate_parent_ticket(
            db=db,
            parent_ticket_id=request.parent_ticket_id,
            project_id=project.id,
        )

    if request.assigned_to:
        await validate_ticket_assignee(
            db=db,
            project_id=project.id,
            user_id=request.assigned_to,
        )

    ticket_number = await _generate_ticket_number(
        db=db,
        project=project,
    )

    ticket = Ticket(
        organization_id=project.organization_id,
        project_id=project.id,
        parent_ticket_id=request.parent_ticket_id,
        assigned_to=request.assigned_to,
        title=request.title,
        description=request.description,
        priority=request.priority.value,
        status=TicketStatus.TODO.value,
        type=request.type.value,
        ticket_number=ticket_number,
        difficulty=request.difficulty,
        expected_start_date=request.expected_start_date,
        expected_end_date=request.expected_end_date,
        actual_start_date=request.actual_start_date,
        actual_end_date=request.actual_end_date,
        reason_for_delay=request.reason_for_delay,
        hours_logged=request.hours_logged or 0,
        demo_link=request.demo_link,
    )
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return TicketResponse(
        success=True,
        status_code=status.HTTP_201_CREATED,
        message="Ticket created successfully.",
        data=TicketSchema.model_validate(ticket),
    )


async def list_project_tickets(
    db: AsyncSession,
    project_id: UUID,
    current_user: User,
) -> TicketListResponse:

    await validate_project_membership(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    result = await db.scalars(
        select(Ticket)
        .where(Ticket.project_id == project_id)
        .order_by(Ticket.created_at.desc())
    )

    tickets = result.all()

    return TicketListResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Tickets retrieved successfully.",
        data=[TicketSchema.model_validate(ticket) for ticket in tickets],
    )


async def get_project_ticket(
    db: AsyncSession,
    ticket_id: UUID,
    current_user: User,
) -> TicketResponse:
    """
    Returns a single ticket.
    """

    # Validate ticket exists
    ticket = await validate_ticket(
        db=db,
        ticket_id=ticket_id,
    )

    # Validate user belongs to the project
    await validate_project_membership(
        db=db,
        project_id=ticket.project_id,
        user_id=current_user.id,
    )

    return TicketResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Ticket retrieved successfully.",
        data=TicketSchema.model_validate(ticket),
    )


async def update_project_ticket(
    db: AsyncSession,
    ticket_id: UUID,
    request: UpdateTicketRequest,
    current_user: User,
) -> TicketResponse:
    """
    Update an existing ticket.
    """

    # Validate ticket
    ticket = await validate_ticket(
        db=db,
        ticket_id=ticket_id,
    )

    # Validate project membership
    project, membership, role, permissions = await validate_project_membership(
        db=db,
        project_id=ticket.project_id,
        user_id=current_user.id,
    )

    # Validate role / permission
    validate_project_role(
        role=role,
        allowed_roles=[
            ProjectRole.PROJECT_OWNER,
            ProjectRole.PROJECT_ADMIN,
            ProjectRole.ENGINEER,
            ProjectRole.QA,
            ProjectRole.REPORTER,
        ],
    )

    # Only include fields explicitly sent by the client
    update_data = request.model_dump(exclude_unset=True)

    # Validate assignee if changed
    if "assigned_to" in update_data:
        await validate_ticket_assignee(
            db=db,
            project_id=project.id,
            user_id=update_data["assigned_to"],
        )

    # Validate parent ticket if changed
    if "parent_ticket_id" in update_data:
        await validate_parent_ticket(
            db=db,
            parent_ticket_id=update_data["parent_ticket_id"],
            project_id=project.id,
            current_ticket_id=ticket.id,
        )

    # Update enum fields
    enum_fields = {
        "priority",
        "status",
        "type",
    }

    for field, value in update_data.items():
        if field in enum_fields and value is not None:
            value = value.value

        setattr(ticket, field, value)

    await db.commit()
    await db.refresh(ticket)

    return TicketResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Ticket updated successfully.",
        data=TicketSchema.model_validate(ticket),
    )


async def delete_project_ticket(
    db: AsyncSession,
    ticket_id: UUID,
    current_user: User,
) -> APIResponse[None]:

    ticket = await validate_ticket(
        db=db,
        ticket_id=ticket_id,
    )
    project, membership, role, permissions = await validate_project_membership(
        db=db,
        project_id=ticket.project_id,
        user_id=current_user.id,
    )
    validate_project_role(
        role=role,
        allowed_roles=[
            ProjectRole.PROJECT_OWNER,
            ProjectRole.PROJECT_ADMIN,
        ],
    )

    await db.delete(ticket)
    await db.commit()

    return APIResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Ticket deleted successfully.",
    )

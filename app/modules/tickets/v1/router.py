from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models import User
from app.modules.auth.deps import get_current_user
from app.modules.tickets.v1.schemas import (
    CreateTicketRequest,
    UpdateTicketRequest,
    TicketResponse,
    TicketListResponse,
)

from app.modules.tickets.v1.service import (
    create_project_ticket,
    list_project_tickets,
    get_project_ticket,
    update_project_ticket,
    delete_project_ticket,
    list_milestone_tickets
)

router = APIRouter(
    prefix="/v1",
    tags=["Ticket"],
)


@router.post(
    "/projects/{project_id}/tickets",
    response_model=TicketResponse,
)
async def create_ticket(
    project_id: UUID,
    request: CreateTicketRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_project_ticket(
        db=db,
        project_id=project_id,
        request=request,
        current_user=current_user,
    )


@router.get(
    "/projects/{project_id}/tickets",
    response_model=TicketListResponse,
)
async def list_project_ticket(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_project_tickets(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
)
async def get_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_project_ticket(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
    )


@router.put(
    "/tickets/{ticket_id}",
    response_model=TicketResponse,
)
async def update_ticket(
    ticket_id: UUID,
    request: UpdateTicketRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_project_ticket(
        db=db,
        ticket_id=ticket_id,
        request=request,
        current_user=current_user,
    )


@router.delete(
    "/tickets/{ticket_id}",
)
async def delete_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await delete_project_ticket(
        db=db,
        ticket_id=ticket_id,
        current_user=current_user,
    )


@router.get(
    "/projects/{project_id}/milestones/{milestone_name}/tickets",
    response_model=TicketListResponse,
)
async def list_milestone_tickets_endpoint(
    project_id: UUID,
    milestone_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_milestone_tickets(
        db=db,
        project_id=project_id,
        milestone_name=milestone_name,
        current_user=current_user,
    )
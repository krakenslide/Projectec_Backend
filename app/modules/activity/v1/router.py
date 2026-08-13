from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.user import User
from app.modules.auth.deps import get_current_user

from .schemas import TicketActivitiesResponse
from .service import list_ticket_activities


router = APIRouter(
    prefix="/v1/activities",
    tags=["Activities"],
)


@router.get(
    "/tickets/{ticket_id}",
    response_model=TicketActivitiesResponse,
)
async def list_ticket_activities_endpoint(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_ticket_activities(
        db=db,
        ticket_id=ticket_id,
    )
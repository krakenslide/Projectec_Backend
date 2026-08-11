from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.modules.auth.deps import get_current_user
from app.modules.tickets.v1.schemas import TicketResponse as IssueResponse

from .schemas import DashboardSummaryReponse
from .service import get_dashboard_summary, get_my_assigned_issues, get_recent_issues

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryReponse)
async def summary(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await get_dashboard_summary(db, current_user.id)

@router.get("/my-issues", response_model=list[IssueResponse])
async def my_issues(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await get_my_assigned_issues(db, current_user.id)

@router.get("/recent-issues", response_model=list[IssueResponse])
async def recent_issues(limit: int = 10, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    safe_limit = min(max(limit, 1), 50)
    return await get_recent_issues(db, current_user.id, safe_limit)
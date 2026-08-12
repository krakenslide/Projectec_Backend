from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.user import User
from app.modules.auth.deps import get_current_user

from .schemas import DeveloperDailySummaryResponse
from fastapi.responses import StreamingResponse

from .service import (
    generate_organization_daily_report,
    get_developer_daily_summary,
)


router = APIRouter(
    prefix="/v1/analytics",
    tags=["Developer Analytics"],
)


@router.get(
    "/{organization_id}/developers/{user_id}/daily-summary",
    response_model=DeveloperDailySummaryResponse,
)
async def get_developer_daily_summary_endpoint(
    organization_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_developer_daily_summary(
        db=db,
        organization_id=organization_id,
        user_id=user_id,
        current_user=current_user,
    )


@router.get(
    "/{organization_id}/daily-summary/excel",
)
async def get_organization_daily_summary_excel(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file = await generate_organization_daily_report(
        db=db,
        organization_id=organization_id,
        current_user=current_user,
    )

    return StreamingResponse(
        file,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                "attachment; "
                'filename="Daily Engineer Report.xlsx"'
            )
        },
    )
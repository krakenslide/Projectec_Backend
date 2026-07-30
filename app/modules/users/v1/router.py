from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db
from app.modules.auth.deps import get_current_user
from app.modules.users.v1.schemas import (
    UserListRequest,
    UserListResponse,
)
from app.modules.users.v1.service import list_users
from app.models import User

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=UserListResponse,
    summary="List users",
    description=(
        "Retrieve users. Optionally filter by organization, project or search text."
    ),
)
async def get_users(
    request: Annotated[UserListRequest, Depends()],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserListResponse:
    return await list_users(
        db=db,
        request=request,
        current_user=current_user,
    )

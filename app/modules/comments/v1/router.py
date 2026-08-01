from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.core.schemas import APIResponse
from app.modules.auth.deps import get_current_user
from app.models.user import User

from .schemas import (
    CommentCreateRequest,
    CommentListResponse,
    CommentResponse,
    CommentUpdateRequest,
)
from .service import (
    create_comment,
    delete_comment,
    get_comment,
    list_comments,
    update_comment,
)

router = APIRouter(
    prefix="/v1/tickets/{ticket_id}/comments",
    tags=["Comments"],
)



@router.post(
    "",
    response_model=APIResponse[CommentResponse],
)
async def create_comment_endpoint(
    ticket_id: UUID,
    data: CommentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await create_comment(
        db=db,
        ticket_id=ticket_id,
        data=data,
        current_user_id=current_user.id,
    )


@router.get(
    "",
    response_model=APIResponse[CommentListResponse],
)
async def list_comments_endpoint(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await list_comments(
        db=db,
        ticket_id=ticket_id,
        current_user_id=current_user.id,
    )


@router.put(
    "/{comment_id}",
    response_model=APIResponse[CommentResponse],
)
async def update_comment_endpoint(
    ticket_id: UUID,
    comment_id: UUID,
    data: CommentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await update_comment(
        db=db,
        ticket_id=ticket_id,
        comment_id=comment_id,
        data=data,
        current_user_id=current_user.id,
    )

@router.get(
    "/{comment_id}",
    response_model=APIResponse[CommentResponse],
)
async def get_comment_endpoint(
    ticket_id: UUID,
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await get_comment(
        db=db,
        ticket_id=ticket_id,
        comment_id=comment_id,
        current_user_id=current_user.id,
    )

@router.delete(
    "/{comment_id}",
    response_model=APIResponse[None],
)
async def delete_comment_endpoint(
    ticket_id: UUID,
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await delete_comment(
        db=db,
        ticket_id=ticket_id,
        comment_id=comment_id,
        current_user_id=current_user.id,
    )
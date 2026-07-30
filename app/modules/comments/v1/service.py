from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import APIResponse
from app.models.comment import Comment
from app.models.ticket import Ticket

from .schemas import (
    CommentCreateRequest,
    CommentListResponse,
    CommentResponse,
    CommentUpdateRequest,
)

async def _validate_ticket(
    db: AsyncSession,
    ticket_id: UUID,
) -> Ticket:

    ticket = await db.scalar(
        select(Ticket).where(
            Ticket.id == ticket_id
        )
    )

    if ticket is None:
        raise ValueError("Ticket not found.")

    return ticket


async def _validate_comment(
    db: AsyncSession,
    ticket_id: UUID,
    comment_id: UUID,
) -> Comment:

    comment = await db.scalar(
        select(Comment).where(
            Comment.id == comment_id,
            Comment.ticket_id == ticket_id,
            Comment.is_deleted.is_(False),
        )
    )

    if comment is None:
        raise ValueError("Comment not found.")

    return comment


async def create_comment(
    db: AsyncSession,
    ticket_id: UUID,
    data: CommentCreateRequest,
    current_user_id: UUID,
) -> APIResponse[CommentResponse]:

    await _validate_ticket(
        db=db,
        ticket_id=ticket_id,
    )

    comment = Comment(
        ticket_id=ticket_id,
        description=data.description,
        has_attachment=False,
        created_by=current_user_id,
    )

    db.add(comment)

    await db.commit()
    await db.refresh(comment)

    return APIResponse(
        success=True,
        message="Comment created successfully.",
        status_code= 200,
        data=CommentResponse.model_validate(comment),
    )


async def get_comment(
    db: AsyncSession,
    ticket_id: UUID,
    comment_id: UUID,
    current_user_id: UUID,
) -> APIResponse[CommentResponse]:

    comment = await _validate_comment(
        db=db,
        ticket_id=ticket_id,
        comment_id=comment_id,
    )

    return APIResponse(
        success=True,
        message = "Comments fetched successfully.",
        status_code= 200,
        data=CommentResponse.model_validate(comment),
    )


async def list_comments(
    db: AsyncSession,
    ticket_id: UUID,
    current_user_id: UUID,
) -> APIResponse[CommentListResponse]:

    await _validate_ticket(
        db=db,
        ticket_id=ticket_id,
    )

    comments = (
        await db.scalars(
            select(Comment)
            .where(
                Comment.ticket_id == ticket_id,
                Comment.is_deleted.is_(False),
            )
            .order_by(Comment.created_at.asc())
        )
    ).all()

    return APIResponse(
        success=True,
        status_code= 200,
        message = "Comment fetched successfully.",
        data=CommentListResponse(
            comments=[
                CommentResponse.model_validate(comment)
                for comment in comments
            ]
        ),
    )


async def update_comment(
    db: AsyncSession,
    ticket_id: UUID,
    comment_id: UUID,
    data: CommentUpdateRequest,
    current_user_id: UUID,
) -> APIResponse[CommentResponse]:

    comment = await _validate_comment(
        db=db,
        ticket_id=ticket_id,
        comment_id=comment_id,
    )

    comment.description = data.description
    comment.updated_by = current_user_id

    await db.commit()
    await db.refresh(comment)

    return APIResponse(
        success=True,
        message="Comment updated successfully.",
        status_code= 200,
        data=CommentResponse.model_validate(comment),
    )


async def delete_comment(
    db: AsyncSession,
    ticket_id: UUID,
    comment_id: UUID,
    current_user_id: UUID,
) -> APIResponse[None]:

    comment = await _validate_comment(
        db=db,
        ticket_id=ticket_id,
        comment_id=comment_id,
    )

    comment.is_deleted = True
    comment.deleted_at = datetime.now(UTC)
    comment.deleted_by = current_user_id

    await db.commit()

    return APIResponse(
        success=True,
        status_code= 200,
        message="Comment deleted successfully.",
        data = None,
    )
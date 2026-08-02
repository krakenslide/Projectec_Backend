from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import APIResponse
from app.models.comment import Comment
from app.models.ticket import Ticket
from app.models.user import User

from app.modules.notification.v1.service import create_notifications
from app.modules.notification.v1.schemas import NotificationCreate
from app.modules.notification.v1.enum import NotificationType
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


def _comment_response(comment: Comment, user: User | None) -> CommentResponse:
    return CommentResponse(
        id=comment.id,
        ticket_id=comment.ticket_id,
        description=comment.description,
        has_attachment=comment.has_attachment,
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        created_by=comment.created_by,
        name=user.name if user else None,
        email=user.email if user else None,
        updated_by=comment.updated_by,
    )


# async def create_comment(
#     db: AsyncSession,
#     ticket_id: UUID,
#     data: CommentCreateRequest,
#     current_user_id: UUID,
# ) -> APIResponse[CommentResponse]:

#     await _validate_ticket(
#         db=db,
#         ticket_id=ticket_id,
#     )

#     comment = Comment(
#         ticket_id=ticket_id,
#         description=data.description,
#         has_attachment=False,
#         created_by=current_user_id,
#     )

#     db.add(comment)

#     await db.commit()
#     await db.refresh(comment)

#     user = await db.scalar(select(User).where(User.id == comment.created_by))

#     return APIResponse(
#         success=True,
#         message="Comment created successfully.",
#         status_code= 200,
#         data=_comment_response(comment, user),
#     )


async def create_comment(
    db: AsyncSession,
    ticket_id: UUID,
    data: CommentCreateRequest,
    current_user_id: UUID,
) -> APIResponse[CommentResponse]:

    ticket = await _validate_ticket(
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
    
    # Generates comment.id
    await db.flush()

    notification_requests = []

    for tagged_user_id in set(data.tagged_users):
        if tagged_user_id == current_user_id:
            continue

        notification_requests.append(
            NotificationCreate(
                organization_id=ticket.organization_id,
                project_id=ticket.project_id,
                ticket_id=ticket.id,
                recipient_user_id=tagged_user_id,
                actor_user_id=current_user_id,
                notification_type=NotificationType.MENTION,
                title="You were mentioned",
                message="You were mentioned in a comment.",
                payload={
                    "comment_id": str(comment.id),
                },
                created_by=current_user_id,
            )
        )

    if notification_requests:
        await create_notifications(
            db=db,
            notifications=notification_requests,
        )

    await db.commit()

    await db.refresh(comment)

    user = await db.scalar(
        select(User)
        .where(User.id == comment.created_by)
    )

    return APIResponse(
        success=True,
        message="Comment created successfully.",
        status_code=200,
        data=_comment_response(comment, user),
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

    user = await db.scalar(select(User).where(User.id == comment.created_by))

    return APIResponse(
        success=True,
        message = "Comments fetched successfully.",
        status_code= 200,
        data=_comment_response(comment, user),
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
        await db.execute(
            select(Comment, User)
            .outerjoin(User, User.id == Comment.created_by)
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
            comments=[_comment_response(comment, user) for comment, user in comments]
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

    user = await db.scalar(select(User).where(User.id == comment.created_by))

    return APIResponse(
        success=True,
        message="Comment updated successfully.",
        status_code= 200,
        data=_comment_response(comment, user),
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
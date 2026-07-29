from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.schemas import APIResponse
from app.models.user import User
from app.models.user_project import UserProject
from app.models.user_organization import UserOrganization
from app.modules.users.v1.schemas import (
    UserListRequest,
    UserListResponse,
    UserSchema,
)


async def list_users(
    db: AsyncSession,
    request: UserListRequest,
    current_user: User,
) -> UserListResponse:
    
    stmt = select(User).distinct()

    if request.organization_id:
        stmt = (
            stmt.join(
                UserOrganization,
                UserOrganization.user_id == User.id,
            )
            .where(
                UserOrganization.organization_id == request.organization_id
            )
        )

    if request.project_id:
        stmt = (
            stmt.join(
                UserProject,
                UserProject.user_id == User.id,
            )
            .where(
                UserProject.project_id == request.project_id
            )
        )

    if request.search:
        search = f"%{request.search}%"

        stmt = stmt.where(
            or_(
                User.first_name.ilike(search),
                User.last_name.ilike(search),
                User.email.ilike(search),
            )
        )

    stmt = (
        stmt.order_by(User.name)
        .offset((request.page - 1) * request.page_size)
        .limit(request.page_size)
    )

    users = (await db.scalars(stmt)).all()

    print(users)

    return UserListResponse(
        success=True,
        status_code=200,
        message="Users fetched successfully.",
        data=[
            UserSchema.model_validate(user)
            for user in users
        ],
    )
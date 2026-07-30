from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import re
from app.models import Organization
from app.models import User
from app.models.role import Role
from app.models.user_organization import UserOrganization
from app.modules.organizations.v1.schemas import (
    CreateOrganizationRequest,
    OrganizationResponse,
    OrganizationMemberUserResponse,
    OrganizationMemberResponse,
)
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_organization import UserOrganization

from app.modules.helpers.get_permissions import get_user_permissions
from app.modules.organizations.rbac.permissions import PermissionName
from app.modules.organizations.rbac.roles import ProjectRole, OrganizationRole
from app.modules.organizations.rbac.seed_data import (
    DEFAULT_ORGANIZATION_ROLE_PERMISSIONS,
    DEFAULT_PROJECT_ROLE_PERMISSIONS,
)

from app.modules.organizations.v1.schemas import (
    CreateOrganizationRequest,
    OrganizationResponse,
)


# Create the organization
# Fetch the Global Organization Owner role
# Create the UserOrganization mapping
async def create_organization(
    db: AsyncSession,
    request: CreateOrganizationRequest,
    current_user_id,
) -> OrganizationResponse:

    existing = await db.scalar(
        select(Organization).where(Organization.name == request.name)
    )

    if existing:
        return OrganizationResponse(
            success=False,
            status_code=409,
            message="Organization already exists.",
            data=None,
        )

    try:
        organization = Organization(
            name=request.name,
            description=request.description,
            created_by=current_user_id,
        )

        db.add(organization)
        await db.flush()

        owner_role = await db.scalar(
            select(Role).where(Role.name == OrganizationRole.OWNER.value)
        )

        if owner_role is None:
            raise ValueError("Organization Owner role has not been seeded.")

        db.add(
            UserOrganization(
                user_id=current_user_id,
                organization_id=organization.id,
                role_id=owner_role.id,
                created_by=current_user_id,
            )
        )

        await db.commit()
        await db.refresh(organization)

        return OrganizationResponse(
            success=True,
            status_code=201,
            message="Organization created successfully.",
            data=None,
        )

    except IntegrityError:
        import traceback

        traceback.print_exc()

        await db.rollback()

        return OrganizationResponse(
            success=False,
            status_code=409,
            message="Integrity constraint violated.",
            data=None,
        )

    except Exception as e:
        import traceback

        traceback.print_exc()

        await db.rollback()

        return OrganizationResponse(
            success=False,
            status_code=500,
            message=str(e),
            data=None,
        )


async def get_organizations_for_user(
    db: AsyncSession,
    user_id,
) -> OrganizationResponse:

    result = await db.scalars(
        select(Organization)
        .join(
            UserOrganization,
            UserOrganization.organization_id == Organization.id,
        )
        .where(UserOrganization.user_id == user_id)
    )

    organizations = result.all()

    data = [
        {
            "id": str(org.id),
            "name": org.name,
            "created_at": org.created_at,
            "updated_at": org.updated_at,
        }
        for org in organizations
    ]

    return OrganizationResponse(
        success=True,
        status_code=200,
        message="Organizations fetched successfully.",
        data=data,
    )


async def get_organization_membership(
    db: AsyncSession,
    organization_id,
    user_id,
):
    result = await db.execute(
        select(UserOrganization, Role)
        .join(
            Role,
            Role.id == UserOrganization.role_id,
        )
        .where(
            UserOrganization.organization_id == organization_id,
            UserOrganization.user_id == user_id,
        )
    )

    row = result.first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Membership not found",
        )

    membership, role = row

    return membership, role


async def require_organization_admin_or_owner(
    db: AsyncSession, organization_id, user_id
):
    membership, role = await get_organization_membership(db, organization_id, user_id)

    if role not in ["OWNER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return True


ROLE_NAME_MAP = {
    "OWNER": "Owner",
    "ADMINISTRATOR": "Administrator",
    "MEMBER": "Member",
}


async def add_organization_member(
    db: AsyncSession, organization_id, data, current_user_id
):
    if (
        await require_organization_admin_or_owner(db, organization_id, current_user_id)
        == True
    ):
        user_result = await db.execute(select(User).where(User.email == data.email))
        user = user_result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        existing_membership_result = await db.execute(
            select(UserOrganization)
            .where(UserOrganization.organization_id == organization_id)
            .where(UserOrganization.user_id == user.id)
        )

        existing_membership = existing_membership_result.scalar_one_or_none()

        if existing_membership:
            raise HTTPException(
                status_code=400, detail="User is already a member of the organization"
            )

        role = await db.scalar(
            select(Role).where(Role.name == ROLE_NAME_MAP[data.role])
        )

        member = UserOrganization(
            organization_id=organization_id,
            user_id=user.id,
            role_id=role.id,
        )

        db.add(member)
        await db.commit()
        await db.refresh(member)
        return member
    else:
        raise HTTPException(
            status_code=401,
            detail="User does not have the required permissions to add project members.",
        )


async def list_organization_members(
    db: AsyncSession,
    organization_id,
    current_user_id,
):

    result = await db.execute(
        select(
            User,
            Role,
        )
        .join(
            UserOrganization,
            User.id == UserOrganization.user_id,
        )
        .join(
            Role,
            Role.id == UserOrganization.role_id,
        )
        .where(UserOrganization.organization_id == organization_id)
    )

    members = []

    for user, role in result.all():

        members.append(
            OrganizationMemberUserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role_id=role.id,
                role_name=role.name,
            )
        )

    return members


async def remove_organization_member(
    db: AsyncSession,
    organization_id,
    user_id,
    current_user_id,
):

    membership = await db.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == organization_id,
            UserOrganization.user_id == user_id,
        )
    )

    if membership is None:
        return OrganizationMemberResponse(
            success=False,
            status_code=404,
            message="Member not found.",
            data=None,
        )

    if user_id == current_user_id:
        return OrganizationMemberResponse(
            success=False,
            status_code=400,
            message="Use the leave organization endpoint instead.",
            data=None,
        )

    await db.delete(membership)
    await db.commit()

    return OrganizationMemberResponse(
        success=True,
        status_code=200,
        message="Member removed successfully.",
        data=None,
    )

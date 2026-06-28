from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import re
from app.models import Organization 
from app.models import Organization  as OrganizationMember
from app.models import User
from app.models.role import Role
from app.models.user_organization import UserOrganization
from app.modules.organizations.v1.schemas import CreateOrganizationRequest, OrganizationResponse
from sqlalchemy.exc import IntegrityError

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_organization import UserOrganization

from app.modules.organizations.rbac.permissions import PermissionName
from app.modules.organizations.rbac.roles import RoleName
from app.modules.organizations.rbac.seed_data import (
    DEFAULT_ROLE_PERMISSIONS,
)

from app.modules.organizations.v1.schemas import (
    CreateOrganizationRequest,
    OrganizationResponse,
)

async def create_organization(
    db: AsyncSession,
    request: CreateOrganizationRequest,
    current_user_id,
) -> OrganizationResponse:

    existing = await db.scalar(
        select(Organization).where(
            Organization.name == request.name
        )
    )

    if existing:
        return OrganizationResponse(
            success=False,
            status_code=409,
            message="Organization already exists.",
            data=None,
        )

    try:

        # =====================================================
        # Create Organization
        # =====================================================

        organization = Organization(
            name=request.name,
            description=request.description,
            created_by=current_user_id,
        )

        db.add(organization)

        await db.flush()

        # =====================================================
        # Load Permissions
        # =====================================================

        permissions = await db.scalars(
            select(Permission)
        )

        permission_map = {
            permission.name: permission
            for permission in permissions
        }

        # =====================================================
        # Create Default Roles
        # =====================================================

        roles = {}

        for role_name in RoleName:

            role = Role(
                organization_id=organization.id,
                name=role_name.value,
                created_by=current_user_id,
            )

            db.add(role)

            await db.flush()

            roles[role_name] = role

        # =====================================================
        # Assign Permissions to Roles
        # =====================================================

        for role_name, permission_names in DEFAULT_ROLE_PERMISSIONS.items():

            role = roles[role_name]

            for permission_name in permission_names:

                permission = permission_map.get(
                    permission_name.value
                )

                if permission is None:
                    raise ValueError(
                        f"Permission '{permission_name.value}' not found."
                    )

                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                        created_by=current_user_id,
                    )
                )

        await db.flush()

        # =====================================================
        # Make Creator Owner
        # =====================================================

        db.add(
            UserOrganization(
                user_id=current_user_id,
                organization_id=organization.id,
                role_id=roles[RoleName.OWNER].id,
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

        await db.rollback()

        return OrganizationResponse(
            success=False,
            status_code=409,
            message="Integrity constraint violated.",
            data=None,
        )

    except Exception as e:

        await db.rollback()

        return OrganizationResponse(
            success=False,
            status_code=500,
            message=str(e),
            data=None,
        )

async def get_organizations_for_user(db: AsyncSession, user_id):
    result = await db.execute(
        select(Organization)
        .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
        .where(OrganizationMember.user_id == user_id)
        .order_by(Organization.created_at.desc())
    )
    
    return result.scalars().all()

async def get_organization_for_user_by_id(db: AsyncSession, organization_id, user_id):
    result = await db.execute(
        select(Organization)
        .join(OrganizationMember, OrganizationMember.organization_id == Organization.id)
        .where(Organization.id == organization_id)
        .where(OrganizationMember.user_id == user_id)
    )
    
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    return organization


async def get_organization_membership(db: AsyncSession, organization_id, user_id):
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == organization_id)
        .where(OrganizationMember.user_id == user_id)
    )
    
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    return membership

async def require_organization_admin(db: AsyncSession, organization_id, user_id):
    membership = await get_organization_membership(db, organization_id, user_id)

    if membership.role not in ["OWNER", "ADMIN"]:
        raise HTTPException(status_code=403, detail="Not allowed")

    return membership

async def add_organization_member(db: AsyncSession, organization_id, data, current_user_id):
    await require_organization_admin(db, organization_id, current_user_id)
    user_result = await db.execute(select(User).where(User.email == data.email))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_membership_result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == organization_id)
        .where(OrganizationMember.user_id == user.id)
    )
    
    existing_membership = existing_membership_result.scalar_one_or_none()
    
    if existing_membership:
        raise HTTPException(status_code=400, detail="User is already a member of the organization")
    
    member = OrganizationMember(
        organization_id=organization_id,
        user_id=user.id,
        role=data.role,
    )
    
    db.add(member)
    await db.commit()
    await db.refresh(member)
    
    return member


async def list_organization_members(db: AsyncSession, organization_id, current_user_id):
    await require_organization_admin(db, organization_id, current_user_id)

    result = await db.execute(
        select(
            OrganizationMember.id,
            OrganizationMember.organization_id,
            OrganizationMember.user_id,
            OrganizationMember.role,
            User.email,
            OrganizationMember.created_at,
            OrganizationMember.updated_at,
        )
        .join(User, User.id == OrganizationMember.user_id)
        .where(OrganizationMember.organization_id == organization_id)
        .order_by(OrganizationMember.created_at.asc())
    )
    
    rows = result.all()
    
    return [
        {
            "id": row.id,
            "organization_id": row.organization_id,
            "user_id": row.user_id,
            "role": row.role,
            "email": row.email,
            "created_at": row.created_at,
            "updated_at": row.updated_at,
        }
        for row in rows
    ]
    
async def remove_organization_member(db: AsyncSession, organization_id, user_id_to_remove, current_user_id):
    await require_organization_admin(db, organization_id, current_user_id)

    if user_id_to_remove == current_user_id:
        raise HTTPException(status_code=400, detail="You cannot remove yourself from the organization")
    
    result = await db.execute(
        select(OrganizationMember)
        .where(OrganizationMember.organization_id == organization_id)
        .where(OrganizationMember.user_id == user_id_to_remove)
    )
    
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(status_code=404, detail="Membership not found")
    
    await db.delete(member)
    await db.commit()
    
    return {"message": "Member removed successfully"}
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import re
from .models import Organization, OrganizationMember
from app.modules.auth.models import User

def generate_slug(name: str) -> str:
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")

    return slug or "organization"

async def create_organization(db: AsyncSession, data, user_id):
    base_slug = generate_slug(data.name)
    slug = base_slug
    counter = 2

    while True:
        existing_result = await db.execute(
            select(Organization).where(Organization.slug == slug)
        )
        existing = existing_result.scalar_one_or_none()

        if not existing:
            break

        slug = f"{base_slug}-{counter}"
        counter += 1

    organization = Organization(
        name=data.name,
        slug=slug,
        owner_id=user_id,
    )

    db.add(organization)
    await db.flush()

    member = OrganizationMember(
        organization_id=organization.id,
        user_id=user_id,
        role="OWNER",
    )

    db.add(member)
    await db.commit()
    await db.refresh(organization)

    return organization
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
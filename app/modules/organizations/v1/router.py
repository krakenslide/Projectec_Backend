from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.modules.auth.deps import get_current_user

from .schemas import CreateOrganizationRequest, OrganizationResponse, AddOrganizationMemberRequest, OrganizationMemberResponse, OrganizationMemberUserResponse
from ..service import (create_organization, get_organizations_for_user, get_organization_for_user_by_id, add_organization_member, list_organization_members, remove_organization_member) 

router = APIRouter(prefix="/v1/organizations", tags=["Organizations"])

@router.post("/", response_model=OrganizationResponse)
async def create(data: CreateOrganizationRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await create_organization(db, data, current_user.id)

@router.get("/", response_model=list[OrganizationResponse])
async def list_organizations(db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await get_organizations_for_user(db, current_user.id)

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(organization_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await get_organization_for_user_by_id(db, organization_id, current_user.id)

@router.post("/{organization_id}/members", response_model=OrganizationMemberResponse)
async def add_member(organization_id: UUID, data: AddOrganizationMemberRequest, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await add_organization_member(db = db, organization_id = organization_id, data = data, current_user_id = current_user.id)

@router.get("/{organization_id}/members", response_model=list[OrganizationMemberUserResponse])
async def list_members(organization_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await list_organization_members(db, organization_id, current_user.id)

@router.delete("/{organization_id}/members/{user_id}")
async def remove_member(organization_id: UUID, user_id: UUID, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    return await remove_organization_member(db, organization_id, user_id, current_user.id)
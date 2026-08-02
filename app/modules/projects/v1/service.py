from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Organization, UserOrganization, User
from app.models.project import Project
from app.models.user_project import UserProject
from app.modules.projects.v1.schemas import (
    CreateProjectRequest,
    ProjectSchema,
    UpdateProjectRequest,
    ProjectMemberResponse,
    AddProjectMemberRequest,
    ProjectMemberListResponse,
    UpdateProjectMemberRoleRequest,
    ProjectMemberSchema,
)
from app.models import Role
from app.modules.organizations.rbac.roles import (
    OrganizationRole,
    ProjectRole,
)
from app.core.schemas import APIResponse


async def add_project_member(
    db: AsyncSession,
    project_id,
    data: AddProjectMemberRequest,
    current_user_id,
) -> APIResponse[ProjectMemberSchema]:

    # Validate project exists

    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    # Validate current user belongs to project

    current_membership = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == current_user_id,
        )
    )

    if current_membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this project.",
        )

    current_role = await db.scalar(
        select(Role).where(Role.id == current_membership.role_id)
    )

    if current_role.name not in [
        ProjectRole.PROJECT_OWNER.value,
        ProjectRole.PROJECT_ADMIN.value,
    ]:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to add project members.",
        )

    # Find user

    user = await db.scalar(select(User).where(User.email == data.email))

    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="User not found.",
        )

    # Validate organization membership

    organization_membership = await db.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == project.organization_id,
            UserOrganization.user_id == user.id,
        )
    )

    if organization_membership is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="User is not a member of this organization.",
        )

    # Prevent duplicate membership

    existing_member = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == user.id,
        )
    )

    if existing_member:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="User is already a project member.",
        )

    # Lookup role

    role = await db.scalar(select(Role).where(Role.name == data.role.value))

    if role is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid project role.",
        )

    # Create membership

    member = UserProject(
        project_id=project.id,
        user_id=user.id,
        role_id=role.id,
    )

    db.add(member)

    await db.commit()
    await db.refresh(member)

    return APIResponse(
        success=True,
        status_code=HTTPStatus.CREATED,
        message="Project member added successfully.",
        data=ProjectMemberSchema(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            email=user.email,
                name=user.name,
            role=data.role,
            created_at=member.created_at,
            updated_at=member.updated_at,
        ),
    )


async def list_project_members(
    db: AsyncSession,
    project_id,
    current_user_id,
) -> APIResponse[list[ProjectMemberSchema]]:
    # Validate project exists

    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    # Validate current user belongs to project

    membership = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == current_user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this project.",
        )

    # Fetch members

    result = await db.execute(
        select(
            UserProject,
            User,
            Role,
        )
        .join(
            User,
            User.id == UserProject.user_id,
        )
        .join(
            Role,
            Role.id == UserProject.role_id,
        )
        .where(
            UserProject.project_id == project_id,
        )
        .order_by(
            User.email.asc(),
        )
    )

    members = []

    for membership, user, role in result.all():
        members.append(
            ProjectMemberSchema(
                id=membership.id,
                project_id=membership.project_id,
                user_id=membership.user_id,
                email=user.email,
                name=user.name,
                role=ProjectRole(role.name),
                created_at=membership.created_at,
                updated_at=membership.updated_at,
            )
        )

    return APIResponse(
        success=True,
        status_code=HTTPStatus.OK,
        message="Project members fetched successfully.",
        data=members,
    )


async def update_project_member_role(
    db: AsyncSession,
    project_id,
    user_id,
    data: UpdateProjectMemberRoleRequest,
    current_user_id,
) -> APIResponse[ProjectMemberSchema]:
    # Validate project exists

    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    # Validate current user membership

    current_membership = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == current_user_id,
        )
    )

    if current_membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this project.",
        )

    current_role = await db.scalar(
        select(Role).where(
            Role.id == current_membership.role_id,
        )
    )

    if current_role.name not in [
        ProjectRole.PROJECT_OWNER.value,
        ProjectRole.PROJECT_ADMIN.value,
    ]:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to update project members.",
        )

    # Prevent self role update

    if current_user_id == user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You cannot update your own role.",
        )

    # Fetch member

    member = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == user_id,
        )
    )

    if member is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project member not found.",
        )

    # Fetch target role

    role = await db.scalar(
        select(Role).where(
            Role.name == data.role.value,
        )
    )

    if role is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid role.",
        )

    # Update role

    member.role_id = role.id

    await db.commit()
    await db.refresh(member)

    user = await db.scalar(select(User).where(User.id == member.user_id))

    return APIResponse(
        success=True,
        status_code=HTTPStatus.OK,
        message="Project member role updated successfully.",
        data=ProjectMemberSchema(
            id=member.id,
            project_id=member.project_id,
            user_id=member.user_id,
            email=user.email,
            role=data.role,
            created_at=member.created_at,
            updated_at=member.updated_at,
        ),
    )


async def remove_project_member(
    db: AsyncSession,
    project_id,
    user_id,
    current_user_id,
) -> APIResponse[None]:

    # Validate project exists

    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    # Validate current user membership

    current_membership = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == current_user_id,
        )
    )

    if current_membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this project.",
        )

    current_role = await db.scalar(
        select(Role).where(
            Role.id == current_membership.role_id,
        )
    )

    if current_role.name not in [
        ProjectRole.PROJECT_OWNER.value,
        ProjectRole.PROJECT_ADMIN.value,
    ]:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to remove project members.",
        )

    # Prevent self removal

    if current_user_id == user_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="You cannot remove yourself from the project.",
        )

    # Fetch member

    member = await db.scalar(
        select(UserProject).where(
            UserProject.project_id == project_id,
            UserProject.user_id == user_id,
        )
    )

    if member is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project member not found.",
        )

    await db.delete(member)
    await db.commit()

    return APIResponse(
        success=True,
        status_code=HTTPStatus.OK,
        message="Project member removed successfully.",
        data=None,
    )


async def create_project(
    db: AsyncSession,
    organization_id,
    data: CreateProjectRequest,
    current_user_id,
) -> APIResponse[ProjectSchema]:

    # Validate organization exists

    organization = await db.scalar(
        select(Organization).where(Organization.id == organization_id)
    )

    if organization is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Organization not found.",
        )

    # Validate user belongs to organization

    membership = await db.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == organization_id,
            UserOrganization.user_id == current_user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    # Allow only Owner / Administrator to create projects

    role = await db.scalar(
        select(Role).where(
            Role.id == membership.role_id,
        )
    )

    if role is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Invalid role.",
        )

    if role.name not in [
        OrganizationRole.OWNER.value,
        OrganizationRole.ADMINISTRATOR.value,
    ]:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to create projects.",
        )

    # Check duplicate project name

    existing_project = await db.scalar(
        select(Project).where(
            Project.organization_id == organization_id,
            Project.name == data.name,
        )
    )

    # PROJECT CODE VALIDATION
    if existing_project:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Project with this name already exists.",
        )

    existing_project = await db.scalar(select(Project).where(Project.code == data.code))

    if existing_project:
        raise HTTPException(
            status_code=400,
            detail="Project code already exists.",
        )

    # Create project

    project = Project(
        organization_id=organization_id,
        name=data.name,
        code=data.code,
        description=data.description,
    )

    db.add(project)
    await db.flush()

    # Assign creator as Project Owner

    project_owner_role = await db.scalar(
        select(Role).where(
            Role.name == ProjectRole.PROJECT_OWNER.value,
        )
    )

    if project_owner_role is None:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Project Owner role not found.",
        )

    project_member = UserProject(
        project_id=project.id,
        user_id=current_user_id,
        role_id=project_owner_role.id,
    )

    db.add(project_member)

    await db.commit()
    await db.refresh(project)

    return APIResponse(
        success=True,
        status_code=HTTPStatus.CREATED,
        message="Project created successfully.",
        data=ProjectSchema.model_validate(project),
    )


async def get_projects_for_organization(
    db: AsyncSession,
    organization_id,
    current_user_id,
) -> APIResponse[list[ProjectSchema]]:
    # Validate organization exists

    organization = await db.scalar(
        select(Organization).where(Organization.id == organization_id)
    )

    if organization is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Organization not found.",
        )

    # Validate user belongs to organization

    membership = await db.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == organization_id,
            UserOrganization.user_id == current_user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    #Validate user belongs to project
    user_project_ids = (
        await db.scalars(
            select(UserProject.project_id).where(
                UserProject.user_id == current_user_id
            )
        )
    ).all()
    
    if user_project_ids is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this project.",
        )

    # Fetch projects

    result = await db.scalars(
        select(Project)
        .where(
            Project.organization_id == organization_id,
            Project.id.in_(user_project_ids),
        )
        .order_by(Project.created_at.desc())
    )

    projects = result.all()

    return APIResponse(
        success=True,
        status_code=HTTPStatus.OK,
        message="Projects fetched successfully.",
        data=[ProjectSchema.model_validate(project) for project in projects],
    )


async def get_project(
    db: AsyncSession,
    project_id,
    current_user_id,
) -> APIResponse[ProjectSchema]:

    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    # Validate user belongs to organization

    membership = await db.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == project.organization_id,
            UserOrganization.user_id == current_user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    return APIResponse(
        success=True,
        status_code=HTTPStatus.OK,
        message="Project fetched successfully.",
        data=ProjectSchema.model_validate(project),
    )


async def update_project(
    db: AsyncSession,
    project_id,
    data: UpdateProjectRequest,
    current_user_id,
) -> APIResponse[ProjectSchema]:
    # Fetch project

    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    # Validate user belongs to organization

    membership = await db.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == project.organization_id,
            UserOrganization.user_id == current_user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    # Allow only Owner / Administrator

    role = await db.scalar(
        select(Role).where(
            Role.id == membership.role_id,
        )
    )

    if role.name not in [
        OrganizationRole.OWNER.value,
        OrganizationRole.ADMINISTRATOR.value,
    ]:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to update this project.",
        )

    # Duplicate name check

    if data.name and data.name != project.name:
        existing_project = await db.scalar(
            select(Project).where(
                Project.organization_id == project.organization_id,
                Project.name == data.name,
                Project.id != project.id,
            )
        )

        if existing_project:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Project with this name already exists.",
            )

        project.name = data.name

    if data.description is not None:
        project.description = data.description

    await db.commit()
    await db.refresh(project)

    return APIResponse(
        success=True,
        status_code=HTTPStatus.OK,
        message="Project updated successfully.",
        data=ProjectSchema.model_validate(project),
    )


async def delete_project(
    db: AsyncSession,
    project_id,
    current_user_id,
) -> APIResponse[None]:
    # Fetch project

    project = await db.scalar(select(Project).where(Project.id == project_id))

    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Project not found.",
        )

    # Validate user belongs to organization

    membership = await db.scalar(
        select(UserOrganization).where(
            UserOrganization.organization_id == project.organization_id,
            UserOrganization.user_id == current_user_id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You are not a member of this organization.",
        )

    # Allow only Owner / Administrator

    role = await db.scalar(
        select(Role).where(
            Role.id == membership.role_id,
        )
    )

    if role.name not in [
        OrganizationRole.OWNER.value,
        OrganizationRole.ADMINISTRATOR.value,
    ]:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You don't have permission to delete this project.",
        )

    await db.delete(project)
    await db.commit()

    return APIResponse(
        success=True,
        status_code=HTTPStatus.OK,
        message="Project deleted successfully.",
        data=None,
    )

from sqlalchemy import select
from collections import defaultdict
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user_organization import UserOrganization
from sqlalchemy.ext.asyncio import AsyncSession

async def get_user_permissions(
    db: AsyncSession,
    user_id,
    organization_id,
) -> set[str]:

    result = await db.scalars(
        select(Permission.name)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.id,
        )
        .join(
            UserOrganization,
            UserOrganization.role_id == RolePermission.role_id,
        )
        .where(
            UserOrganization.user_id == user_id,
            UserOrganization.organization_id == organization_id,
        )
        .distinct()
    )
    print("DEBUG1: ",list(set(result.all())))
    import time 
    time.sleep(5)
    print()
    return list(set(result.all()))



async def get_roles_with_permissions(
    db: AsyncSession,
    organization_id,
) -> list[dict]:

    result = await db.execute(
        select(
            Role.name,
            Permission.name,
        )
        .join(
            RolePermission,
            RolePermission.role_id == Role.id,
        )
        .join(
            Permission,
            Permission.id == RolePermission.permission_id,
        )
        .where(
            Role.organization_id == organization_id,
        )
        .order_by(
            Role.name,
            Permission.name,
        )
    )

    roles = defaultdict(list)

    for role_name, permission_name in result:
        roles[role_name].append(permission_name)

    return [
        {
            "role": role_name,
            "permissions": permissions,
        }
        for role_name, permissions in roles.items()
    ]

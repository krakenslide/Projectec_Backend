import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission

from app.modules.organizations.rbac.roles import (
    OrganizationRole,
    ProjectRole,
    RoleType,
)

from app.modules.organizations.rbac.seed_data import (
    DEFAULT_PERMISSIONS,
    DEFAULT_ORGANIZATION_ROLE_PERMISSIONS,
    DEFAULT_PROJECT_ROLE_PERMISSIONS,
)

async def seed_rbac():
    async with AsyncSessionLocal() as db:
        # Seed Permissions
        existing_permissions = (
            await db.scalars(
                select(Permission)
            )
        ).all()
        
        permission_map = {
            permission.name: permission
            for permission in existing_permissions
        }

        permissions_inserted = 0

        for permission_name in DEFAULT_PERMISSIONS:

            if permission_name in permission_map:
                continue

            permission = Permission(
                name=permission_name,
            )

            db.add(permission)
            permissions_inserted += 1

        await db.flush()

        permission_map = {
            permission.name: permission
            for permission in (
                await db.scalars(select(Permission))
            ).all()
        }
        
        # Seed Roles
        existing_roles = (
            await db.scalars(
                select(Role)
            )
        ).all()

        role_map = {
            role.name: role
            for role in existing_roles
        }

        roles_inserted = 0

        # Organization Roles
        for role_name in OrganizationRole:

            if role_name.value in role_map:
                continue

            db.add(
                Role(
                    name=role_name.value,
                    role_type=RoleType.ORGANIZATION,
                )
            )

            roles_inserted += 1

        # Project Roles
        for role_name in ProjectRole:

            if role_name.value in role_map:
                continue

            db.add(
                Role(
                    name=role_name.value,
                    role_type=RoleType.PROJECT,
                )
            )

            roles_inserted += 1

        await db.flush()

        role_map = {
            role.name: role
            for role in (
                await db.scalars(
                    select(Role)
                )
            ).all()
        }

        # Seed Role Permissions
        existing_role_permissions = (
            await db.scalars(
                select(RolePermission)
            )
        ).all()

        existing_pairs = {
            (
                rp.role_id,
                rp.permission_id,
            )
            for rp in existing_role_permissions
        }

        mappings_inserted = 0

        role_permission_mappings = {
            **DEFAULT_ORGANIZATION_ROLE_PERMISSIONS,
            **DEFAULT_PROJECT_ROLE_PERMISSIONS,
        }

        for role_enum, permissions in role_permission_mappings.items():

            role = role_map.get(role_enum.value)

            if role is None:
                raise ValueError(
                    f"Role '{role_enum.value}' not found."
                )

            for permission_enum in permissions:

                permission = permission_map.get(permission_enum.value)

                if permission is None:
                    raise ValueError(
                        f"Permission '{permission_enum.value}' not found."
                    )

                pair = (
                    role.id,
                    permission.id,
                )

                if pair in existing_pairs:
                    continue

                db.add(
                    RolePermission(
                        role_id=role.id,
                        permission_id=permission.id,
                    )
                )

                existing_pairs.add(pair)
                mappings_inserted += 1

        await db.commit()

        print("=" * 50)
        print("RBAC Seed Completed")
        print("=" * 50)
        print(f"Permissions inserted : {permissions_inserted}")
        print(f"Roles inserted       : {roles_inserted}")
        print(f"Mappings inserted    : {mappings_inserted}")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed_rbac())
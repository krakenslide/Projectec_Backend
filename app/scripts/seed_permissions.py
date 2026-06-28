import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.permission import Permission
from app.modules.organizations.rbac.seed_data import DEFAULT_PERMISSIONS


async def seed_permissions():

    async with AsyncSessionLocal() as db:

        existing_permissions = await db.scalars(
            select(Permission)
        )

        existing_permission_names = {
            permission.name
            for permission in existing_permissions
        }

        inserted = 0

        for permission_name in DEFAULT_PERMISSIONS:

            if permission_name in existing_permission_names:
                continue

            db.add(
                Permission(
                    name=permission_name,
                )
            )

            inserted += 1

        await db.commit()

        print(f"Inserted {inserted} permissions.")


if __name__ == "__main__":
    asyncio.run(seed_permissions())
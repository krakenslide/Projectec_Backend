# app/seed/seeders/user_organizations.py

import random

from collections import defaultdict

from sqlalchemy.orm import Session
from app.modules.organizations.rbac.roles import ProjectRole, OrganizationRole
from app.models.user_organization import UserOrganization
from app.scripts.seed.config import (
    MIN_USERS_PER_ORGANIZATION,
    MAX_USERS_PER_ORGANIZATION,
)
from app.scripts.seed.context import SeedContext


def seed_user_organizations(
    db: Session,
    context: SeedContext,
) -> None:
    """
    Create organization memberships.

    Rules:
        - Creator becomes Owner.
        - Up to 2 Administrators.
        - Remaining users become Members.
    """

    memberships: list[UserOrganization] = []

    context.organization_members = defaultdict(list)
    context.organization_owner = {}

    owner_role = context.roles[OrganizationRole.OWNER.value]
    admin_role = context.roles[OrganizationRole.ADMINISTRATOR.value]
    member_role = context.roles[OrganizationRole.MEMBER.value]

    for organization in context.organizations:

        owner = context.user_map[organization.created_by]

        context.organization_owner[organization.id] = owner

        available_users = [
            user
            for user in context.users
            if user.id != owner.id
        ]

        member_count = random.randint(
            MIN_USERS_PER_ORGANIZATION,
            min(MAX_USERS_PER_ORGANIZATION, len(context.users))
        )

        selected_users = random.sample(
            available_users,
            k=max(0, member_count - 1)
        )

        organization_users = [owner] + selected_users

        admin_count = min(2, len(selected_users))
        admins = random.sample(selected_users, admin_count)

        for user in organization_users:

            if user.id == owner.id:
                role = owner_role

            elif user in admins:
                role = admin_role

            else:
                role = member_role

            membership = UserOrganization(
                organization_id=organization.id,
                user_id=user.id,
                role_id=role.id,
            )

            memberships.append(membership)
            context.organization_members[organization.id].append(user)

    db.add_all(memberships)
    db.flush()

    context.user_organizations.extend(memberships)
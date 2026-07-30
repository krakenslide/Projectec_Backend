# app/seed/seeders/user_projects.py

import random
from collections import defaultdict

from sqlalchemy.orm import Session
from app.modules.organizations.rbac.roles import ProjectRole, OrganizationRole

from app.models.user_project import UserProject
from app.scripts.seed.context import SeedContext


PROJECT_MEMBER_ROLES = (
    "Engineer",
    "QA",
    "Reporter",
    "Viewer",
)


def seed_user_projects(
    db: Session,
    context: SeedContext,
) -> None:
    """
    Create project memberships.
    """

    memberships: list[UserProject] = []

    context.project_members = defaultdict(list)
    context.project_owner = {}

    owner_role = context.roles[ProjectRole.PROJECT_OWNER.value]
    admin_role = context.roles[ProjectRole.PROJECT_ADMIN.value]

    for project in context.projects:

        organization_users = context.organization_members[
            project.organization_id
        ]

        owner = context.user_map[project.created_by]

        context.project_owner[project.id] = owner

        available_users = [
            user
            for user in organization_users
            if user.id != owner.id
        ]

        #
        # Select project participants.
        #
        project_size = random.randint(
            max(2, len(organization_users) // 2),
            len(organization_users),
        )

        selected_users = random.sample(
            available_users,
            k=min(project_size - 1, len(available_users)),
        )

        project_users = [owner] + selected_users

        #
        # Administrators
        #
        admin_count = min(2, len(selected_users))
        admins = random.sample(selected_users, admin_count)

        #
        # Remaining Roles
        #
        remaining_users = [
            user
            for user in project_users
            if user not in admins and user != owner
        ]

        assigned_roles = {}

        #
        # Guarantee one engineer
        #
        if remaining_users:
            engineer = random.choice(remaining_users)
            assigned_roles[engineer.id] = context.roles[ProjectRole.ENGINEER.value]

        for user in remaining_users:
          if user.id in assigned_roles:
              continue
          role = random.choice(PROJECT_MEMBER_ROLES)
          assigned_roles[user.id] = context.roles[role]
        #
        # Create memberships
        #
        for user in project_users:

            if user.id == owner.id:
                role = owner_role

            elif user in admins:
                role = admin_role

            else:
                role = assigned_roles[user.id]

            membership = UserProject(
                project_id=project.id,
                user_id=user.id,
                role_id=role.id,
            )

            memberships.append(membership)

            context.project_members[project.id].append(user)

    db.add_all(memberships)
    db.flush()

    context.user_projects.extend(memberships)
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from faker import Faker

from app.models.organization import Organization
from app.models.project import Project
from app.models.role import Role
from app.models.ticket import Ticket
from app.models.user import User
from app.models.user_organization import UserOrganization
from app.models.user_project import UserProject


@dataclass(slots=True)
class SeedContext:
    """
    Shared runtime state between all seeders.

    Each seeder populates this context after inserting records so that
    subsequent seeders don't need to repeatedly query the database.
    """

    faker: Faker = field(default_factory=Faker)

    # Users
    users: list[User] = field(default_factory=list)
    user_map: dict[UUID, User] = field(default_factory=dict)

    # Organizations
    organizations: list[Organization] = field(default_factory=list)
    organization_map: dict[UUID, Organization] = field(default_factory=dict)

    # Organization Memberships
    user_organizations: list[UserOrganization] = field(default_factory=list)
    # Organization Owner
    organization_owner: dict[UUID, User] = field(default_factory=dict)

    # organization_id -> members
    organization_members: dict[UUID, list[UserOrganization]] = field(default_factory=dict)

    # Projects
    projects: list[Project] = field(default_factory=list)
    project_map: dict[UUID, Project] = field(default_factory=dict)

    # Project Memberships
    user_projects: list[UserProject] = field(default_factory=list)
    # Project Owner
    project_owner: dict[UUID, User] = field(default_factory=dict)

    # project_id -> members
    project_members: dict[UUID, list[UserProject]] = field(default_factory=dict)

    # Tickets
    tickets: list[Ticket] = field(default_factory=list)

    roles: dict[str, Role] = field(default_factory=dict)
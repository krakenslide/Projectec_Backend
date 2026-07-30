import random

from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.scripts.seed.context import SeedContext


def seed_organizations(
    db: Session,
    context: SeedContext,
    organization_count: int,
) -> None:
    """
    Seed organizations.

    Each organization is assigned a random creator.
    The creator will later become the organization owner in the
    user_organizations seeder.
    """

    organizations: list[Organization] = []

    for _ in range(organization_count):
        creator = random.choice(context.users)

        organization = Organization(
            name=context.faker.unique.company(),
            description=context.faker.catch_phrase(),
            created_by=creator.id,
            updated_by=creator.id,
        )

        organizations.append(organization)

    db.add_all(organizations)
    db.flush()

    context.organizations.extend(organizations)

    for organization in organizations:
        context.organization_map[organization.id] = organization
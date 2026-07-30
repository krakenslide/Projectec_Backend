# app/seed/seed.py

from sqlalchemy.orm import Session

from app.scripts.seed.context import SeedContext

from app.scripts.seed.master.seed_roles_and_permissions import seed_rbac

from app.scripts.seed.seeders.organizations import seed_organizations
from app.scripts.seed.seeders.projects import seed_projects
from app.scripts.seed.seeders.tickets import seed_tickets
from app.scripts.seed.seeders.user_organizations import seed_user_organizations
from app.scripts.seed.seeders.user_projects import seed_user_projects
from app.scripts.seed.seeders.users import seed_users

from sqlalchemy import select
from app.models.role import Role


def seed_database(
    db: Session,
    *,
    user_count: int,
    organization_count: int,
    ticket_count: int,
) -> None:
    """
    Seed the application database.

    Execution order is important because later entities depend on
    earlier ones.
    """

    context = SeedContext()

    # Master Data
    # seed_rbac(db=db, context=context)
    # NOTE : COMMENTING IT OUT BECAUSE ITS A PART OF OUR PROJECT SETUP CODE

    context.roles = {role.name: role for role in db.scalars(select(Role)).all()}

    # Transactional Data
    seed_users(
        db=db,
        context=context,
        user_count=user_count,
    )

    seed_organizations(
        db=db,
        context=context,
        organization_count=organization_count,
    )

    seed_user_organizations(
        db=db,
        context=context,
    )

    seed_projects(
        db=db,
        context=context,
    )

    seed_user_projects(
        db=db,
        context=context,
    )

    seed_tickets(
        db=db,
        context=context,
        ticket_count=ticket_count,
    )

    db.commit()


if __name__ == "__main__":
    seed_database()

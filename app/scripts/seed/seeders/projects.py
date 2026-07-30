# app/seed/seeders/projects.py

import random
import string

from sqlalchemy.orm import Session

from app.models.project import Project
from app.scripts.seed.config import (
    MAX_PROJECTS_PER_ORGANIZATION,
    MIN_PROJECTS_PER_ORGANIZATION,
    PROJECT_CODE_LENGTH,
)
from app.scripts.seed.context import SeedContext


_generated_codes: set[str] = set()


def generate_project_code() -> str:
    """Generate a unique random project code."""

    while True:
        code = "".join(
            random.choices(
                string.ascii_uppercase,
                k=PROJECT_CODE_LENGTH,
            )
        )

        if code not in _generated_codes:
            _generated_codes.add(code)
            return code


def seed_projects(
    db: Session,
    context: SeedContext,
) -> None:
    """
    Seed projects for every organization.
    """

    projects: list[Project] = []

    for organization in context.organizations:

        owner = context.organization_owner[organization.id]

        project_count = random.randint(
            MIN_PROJECTS_PER_ORGANIZATION,
            MAX_PROJECTS_PER_ORGANIZATION,
        )

        for _ in range(project_count):

            project = Project(
                organization_id=organization.id,
                name=context.faker.bs().title(),
                description=context.faker.sentence(nb_words=12),
                code=generate_project_code(),
                created_by=owner.id,
                updated_by=owner.id,
            )

            projects.append(project)

    db.add_all(projects)
    db.flush()

    context.projects.extend(projects)

    for project in projects:
        context.project_map[project.id] = project
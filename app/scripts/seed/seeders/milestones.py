import random
import string

from sqlalchemy.orm import Session

from app.models.milestone import Milestone
from app.scripts.seed.config import (
    MAX_MILESTONES_PER_PROJECT,
    MIN_MILESTONES_PER_PROJECT,
)
from app.scripts.seed.context import SeedContext


def generate_milestone_names(count: int) -> list[str]:
    """
    Generate unique milestone names such as:

        Milestone A
        Milestone Q
        Milestone X
    """

    letters = random.sample(
        string.ascii_uppercase,
        count,
    )

    return [
        f"Milestone {letter}"
        for letter in letters
    ]


def seed_milestones(
    db: Session,
    context: SeedContext,
) -> None:

    milestones: list[Milestone] = []

    for project in context.projects:

        milestone_count = random.randint(
            MIN_MILESTONES_PER_PROJECT,
            MAX_MILESTONES_PER_PROJECT,
        )

        names = generate_milestone_names(
            milestone_count
        )

        project_milestones: list[Milestone] = []

        for name in names:

            milestone = Milestone(
                project_id=project.id,
                name=name,
                created_by=project.created_by,
                updated_by=project.created_by,
            )

            milestones.append(milestone)
            project_milestones.append(milestone)

        context.project_milestones[
            project.id
        ] = project_milestones

    db.add_all(milestones)
    db.flush()

    context.milestones.extend(milestones)
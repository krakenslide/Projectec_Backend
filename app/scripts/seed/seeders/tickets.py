# app/seed/seeders/tickets.py
import random
from datetime import timedelta

from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.ticket import Ticket
from app.models.user_project import UserProject
from app.modules.organizations.rbac.roles import ProjectRole
from app.models.ticket import Ticket
from app.modules.tickets.enum import (
    TicketPriority,
    TicketStatus,
    TicketType,
)
from app.scripts.seed.config import (
    MIN_TICKETS_PER_PROJECT,
    MAX_TICKETS_PER_PROJECT,
)
from app.scripts.seed.context import SeedContext


def seed_tickets(
    db: Session,
    context: SeedContext,
    ticket_count: int | None = None,
) -> None:
    tickets: list[Ticket] = []

    assignee_role_ids = {
        context.roles[ProjectRole.PROJECT_ADMIN.value].id,
        context.roles[ProjectRole.ENGINEER.value].id,
        context.roles[ProjectRole.QA.value].id,
    }

    reporter_role_ids = {
        context.roles[ProjectRole.PROJECT_OWNER.value].id,
        context.roles[ProjectRole.PROJECT_ADMIN.value].id,
        context.roles[ProjectRole.REPORTER.value].id,
        context.roles[ProjectRole.QA.value].id,
    }

    for project in context.projects:

        memberships = (
            db.query(UserProject).filter(UserProject.project_id == project.id).all()
        )

        assignees = [
            membership.user_id
            for membership in memberships
            if membership.role_id in assignee_role_ids
        ]

        reporters = [
            membership.user_id
            for membership in memberships
            if membership.role_id in reporter_role_ids
        ]

        if not assignees or not reporters:
            continue

        total_tickets = (
            ticket_count
            if ticket_count is not None
            else random.randint(
                MIN_TICKETS_PER_PROJECT,
                MAX_TICKETS_PER_PROJECT,
            )
        )

        for _ in range(total_tickets):

            status = random.choice(list(TicketStatus))
            priority = random.choice(list(TicketPriority))
            ticket_type = random.choice(list(TicketType))

            expected_start = context.faker.date_time_this_year()

            expected_end = expected_start + timedelta(days=random.randint(2, 20))

            actual_start = None
            actual_end = None

            if status != TicketStatus.TODO:
                actual_start = expected_start + timedelta(days=random.randint(0, 2))

            if status in (
                TicketStatus.DONE,
                TicketStatus.CLOSED,
            ):
                actual_end = actual_start + timedelta(days=random.randint(1, 15))

            difficulty = random.randint(1, 100)

            ticket = Ticket(
                organization_id=project.organization_id,
                project_id=project.id,
                title=context.faker.sentence(nb_words=6),
                description=context.faker.paragraph(),
                priority=priority,
                status=status,
                type=ticket_type,
                difficulty=difficulty,
                assigned_to=random.choice(assignees),
                created_by=random.choice(reporters),
                expected_start_date=expected_start,
                expected_end_date=expected_end,
                actual_start_date=actual_start,
                actual_end_date=actual_end,
                hours_logged=max(
                    0,
                    difficulty // 5 + random.randint(-3, 5),
                ),
                demo_link=context.faker.url(),
                ticket_number=context.faker.numerify("############"),
            )

            tickets.append(ticket)

    db.add_all(tickets)
    db.flush()

    context.tickets.extend(tickets)

# app/seed/seeders/tickets.py

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.user_project import UserProject
from app.modules.organizations.rbac.roles import ProjectRole
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

    # ---------------------------------------------------------
    # Roles allowed to receive tickets
    # ---------------------------------------------------------

    assignee_role_ids = {
        context.roles[ProjectRole.PROJECT_ADMIN.value].id,
        context.roles[ProjectRole.ENGINEER.value].id,
        context.roles[ProjectRole.QA.value].id,
    }

    # ---------------------------------------------------------
    # Roles allowed to create tickets
    # ---------------------------------------------------------

    reporter_role_ids = {
        context.roles[ProjectRole.PROJECT_OWNER.value].id,
        context.roles[ProjectRole.PROJECT_ADMIN.value].id,
        context.roles[ProjectRole.REPORTER.value].id,
        context.roles[ProjectRole.QA.value].id,
    }

    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # Process every project
    # ---------------------------------------------------------

    for project in context.projects:

        # -----------------------------------------------------
        # Get project members
        # -----------------------------------------------------

        memberships = (
            db.query(UserProject)
            .filter(
                UserProject.project_id == project.id
            )
            .all()
        )

        # -----------------------------------------------------
        # Users who can be assigned tickets
        # -----------------------------------------------------

        assignees = [
            membership.user_id
            for membership in memberships
            if membership.role_id in assignee_role_ids
        ]

        # -----------------------------------------------------
        # Users who can create/report tickets
        # -----------------------------------------------------

        reporters = [
            membership.user_id
            for membership in memberships
            if membership.role_id in reporter_role_ids
        ]

        if not assignees or not reporters:
            continue

        # -----------------------------------------------------
        # Number of tickets for this project
        # -----------------------------------------------------

        total_tickets = (
            ticket_count
            if ticket_count is not None
            else random.randint(
                MIN_TICKETS_PER_PROJECT,
                MAX_TICKETS_PER_PROJECT,
            )
        )

        # -----------------------------------------------------
        # Milestones belonging ONLY to this project
        # -----------------------------------------------------

        project_milestones = context.project_milestones.get(
            project.id,
            []
        )

        # -----------------------------------------------------
        # Generate tickets
        # -----------------------------------------------------

        for _ in range(total_tickets):

            # -------------------------------------------------
            # Choose realistic ticket scenario
            # -------------------------------------------------

            scenario = random.choices(
                [
                    "completed_on_time",
                    "completed_late",
                    "in_progress",
                    "not_started",
                    "overdue",
                ],
                weights=[
                    25,
                    20,
                    25,
                    15,
                    15,
                ],
                k=1,
            )[0]

            # -------------------------------------------------
            # Generate status based on scenario
            # -------------------------------------------------

            if scenario in (
                "completed_on_time",
                "completed_late",
            ):

                status = random.choice(
                    [
                        TicketStatus.DONE,
                        TicketStatus.CLOSED,
                    ]
                )

            elif scenario == "in_progress":

                status = random.choice(
                    [
                        TicketStatus.IN_PROGRESS,
                        TicketStatus.IN_REVIEW,
                        TicketStatus.TESTING,
                    ]
                )

            elif scenario == "not_started":

                status = TicketStatus.TODO

            else:
                # overdue but not completed
                status = random.choice(
                    [
                        TicketStatus.IN_PROGRESS,
                        TicketStatus.IN_REVIEW,
                        TicketStatus.TESTING,
                    ]
                )

            # -------------------------------------------------
            # Priority / type
            # -------------------------------------------------

            priority = random.choice(
                list(TicketPriority)
            )

            ticket_type = random.choice(
                list(TicketType)
            )

            # -------------------------------------------------
            # Generate realistic dates
            # -------------------------------------------------

            if scenario == "completed_on_time":

                # Expected start 10-30 days ago
                expected_start = (
                    now
                    - timedelta(
                        days=random.randint(10, 30)
                    )
                )

                # Expected duration 3-10 days
                expected_end = (
                    expected_start
                    + timedelta(
                        days=random.randint(3, 10)
                    )
                )

                # Actual start close to expected start
                actual_start = (
                    expected_start
                    + timedelta(
                        days=random.randint(-1, 2)
                    )
                )

                # Finished on or around expected date
                actual_end = (
                    expected_end
                    + timedelta(
                        days=random.randint(-2, 1)
                    )
                )

            elif scenario == "completed_late":

                # Expected to start in the past
                expected_start = (
                    now
                    - timedelta(
                        days=random.randint(15, 35)
                    )
                )

                expected_end = (
                    expected_start
                    + timedelta(
                        days=random.randint(3, 10)
                    )
                )

                # Started slightly late
                actual_start = (
                    expected_start
                    + timedelta(
                        days=random.randint(0, 4)
                    )
                )

                # Finished after expected end
                actual_end = (
                    expected_end
                    + timedelta(
                        days=random.randint(2, 10)
                    )
                )

            elif scenario == "in_progress":

                # Started in the past
                expected_start = (
                    now
                    - timedelta(
                        days=random.randint(5, 20)
                    )
                )

                expected_end = (
                    expected_start
                    + timedelta(
                        days=random.randint(5, 15)
                    )
                )

                actual_start = (
                    expected_start
                    + timedelta(
                        days=random.randint(0, 3)
                    )
                )

                # Still being worked on
                actual_end = None

            elif scenario == "not_started":

                # Starts in the future
                expected_start = (
                    now
                    + timedelta(
                        days=random.randint(2, 15)
                    )
                )

                expected_end = (
                    expected_start
                    + timedelta(
                        days=random.randint(3, 10)
                    )
                )

                actual_start = None
                actual_end = None

            else:
                # -------------------------------------------------
                # OVERDUE
                #
                # Expected completion already happened,
                # but the ticket is still not finished.
                # -------------------------------------------------

                expected_start = (
                    now
                    - timedelta(
                        days=random.randint(15, 30)
                    )
                )

                expected_end = (
                    now
                    - timedelta(
                        days=random.randint(1, 7)
                    )
                )

                actual_start = (
                    expected_start
                    + timedelta(
                        days=random.randint(0, 3)
                    )
                )

                # Still unfinished
                actual_end = None

            # -------------------------------------------------
            # Difficulty
            # -------------------------------------------------

            difficulty = random.randint(
                1,
                100,
            )

            # -------------------------------------------------
            # Milestone assignment
            #
            # Approximately 75% of tickets get a milestone.
            # Approximately 25% remain without one.
            # -------------------------------------------------

            milestone = None

            if (
                project_milestones
                and random.random() < 0.75
            ):
                milestone = random.choice(
                    project_milestones
                )

            # -------------------------------------------------
            # Create ticket
            # -------------------------------------------------

            ticket = Ticket(
                organization_id=project.organization_id,

                project_id=project.id,

                milestone_id=(
                    milestone.id
                    if milestone is not None
                    else None
                ),

                title=context.faker.sentence(
                    nb_words=6
                ),

                description=context.faker.paragraph(),

                priority=priority,

                status=status,

                type=ticket_type,

                difficulty=difficulty,

                assigned_to=random.choice(
                    assignees
                ),

                created_by=random.choice(
                    reporters
                ),

                expected_start_date=expected_start,

                expected_end_date=expected_end,

                actual_start_date=actual_start,

                actual_end_date=actual_end,

                hours_logged=max(
                    0,
                    difficulty // 5
                    + random.randint(-3, 5),
                ),

                demo_link=context.faker.url(),

                ticket_number=context.faker.numerify(
                    "############"
                ),
            )

            tickets.append(ticket)

    # ---------------------------------------------------------
    # Insert tickets
    # ---------------------------------------------------------

    db.add_all(tickets)

    db.flush()

    context.tickets.extend(tickets)

# # app/seed/seeders/tickets.py
# import random
# from datetime import timedelta

# from sqlalchemy.orm import Session
# from app.models.role import Role
# from app.models.ticket import Ticket
# from app.models.user_project import UserProject
# from app.modules.organizations.rbac.roles import ProjectRole
# from app.models.ticket import Ticket
# from app.modules.tickets.enum import (
#     TicketPriority,
#     TicketStatus,
#     TicketType,
# )
# from app.scripts.seed.config import (
#     MIN_TICKETS_PER_PROJECT,
#     MAX_TICKETS_PER_PROJECT,
# )
# from app.scripts.seed.context import SeedContext


# def seed_tickets(
#     db: Session,
#     context: SeedContext,
#     ticket_count: int | None = None,
# ) -> None:
#     tickets: list[Ticket] = []

#     assignee_role_ids = {
#         context.roles[ProjectRole.PROJECT_ADMIN.value].id,
#         context.roles[ProjectRole.ENGINEER.value].id,
#         context.roles[ProjectRole.QA.value].id,
#     }

#     reporter_role_ids = {
#         context.roles[ProjectRole.PROJECT_OWNER.value].id,
#         context.roles[ProjectRole.PROJECT_ADMIN.value].id,
#         context.roles[ProjectRole.REPORTER.value].id,
#         context.roles[ProjectRole.QA.value].id,
#     }

#     for project in context.projects:

#         memberships = (
#             db.query(UserProject).filter(UserProject.project_id == project.id).all()
#         )

#         assignees = [
#             membership.user_id
#             for membership in memberships
#             if membership.role_id in assignee_role_ids
#         ]

#         reporters = [
#             membership.user_id
#             for membership in memberships
#             if membership.role_id in reporter_role_ids
#         ]

#         if not assignees or not reporters:
#             continue

#         total_tickets = (
#             ticket_count
#             if ticket_count is not None
#             else random.randint(
#                 MIN_TICKETS_PER_PROJECT,
#                 MAX_TICKETS_PER_PROJECT,
#             )
#         )

#         for _ in range(total_tickets):

#             status = random.choice(list(TicketStatus))
#             priority = random.choice(list(TicketPriority))
#             ticket_type = random.choice(list(TicketType))

#             milestone = None

#             project_milestones = context.project_milestones.get(
#                 project.id,
#                 []
#             )

#             if project_milestones and random.random() < 0.75:
#                 milestone = random.choice(project_milestones)

#             expected_start = context.faker.date_time_this_year()

#             expected_end = expected_start + timedelta(days=random.randint(2, 20))

#             actual_start = None
#             actual_end = None

#             if status != TicketStatus.TODO:
#                 actual_start = expected_start + timedelta(days=random.randint(0, 2))

#             if status in (
#                 TicketStatus.DONE,
#                 TicketStatus.CLOSED,
#             ):
#                 actual_end = actual_start + timedelta(days=random.randint(1, 15))

#             difficulty = random.randint(1, 100)

#             ticket = Ticket(
#                 organization_id=project.organization_id,
#                 project_id=project.id,
#                 title=context.faker.sentence(nb_words=6),
#                 description=context.faker.paragraph(),
#                 milestone_id=(
#                     milestone.id
#                     if milestone is not None
#                     else None
#                 ),
#                 priority=priority,
#                 status=status,
#                 type=ticket_type,
#                 difficulty=difficulty,
#                 assigned_to=random.choice(assignees),
#                 created_by=random.choice(reporters),
#                 expected_start_date=expected_start,
#                 expected_end_date=expected_end,
#                 actual_start_date=actual_start,
#                 actual_end_date=actual_end,
#                 hours_logged=max(
#                     0,
#                     difficulty // 5 + random.randint(-3, 5),
#                 ),
#                 demo_link=context.faker.url(),
#                 ticket_number=context.faker.numerify("############"),
#             )

#             tickets.append(ticket)

#     db.add_all(tickets)
#     db.flush()

#     context.tickets.extend(tickets)

from datetime import datetime, timezone
from uuid import UUID

from fastapi import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.milestone import Milestone
from app.models.ticket import Ticket
from app.models.user import User
from app.modules.tickets.helpers.helpers import validate_project_membership

from .schemas import (
    MilestoneProgressPoint,
    MilestoneProgressResponse,
    MilestoneSchema,
    ProjectMilestonesResponse,
)


async def list_project_milestones(
    db: AsyncSession,
    project_id: UUID,
    current_user: User,
) -> ProjectMilestonesResponse:

    await validate_project_membership(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    result = await db.scalars(
        select(Milestone)
        .where(
            Milestone.project_id == project_id,
        )
        .order_by(Milestone.name.asc())
    )

    milestones = result.all()

    return ProjectMilestonesResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Project milestones retrieved successfully.",
        data=[
            MilestoneSchema.model_validate(milestone)
            for milestone in milestones
        ],
        count=len(milestones),
    )


async def get_milestone_progress(
    db: AsyncSession,
    project_id: UUID,
    milestone_name: str,
    current_user: User,
) -> MilestoneProgressResponse:

    await validate_project_membership(
        db=db,
        project_id=project_id,
        user_id=current_user.id,
    )

    milestone = await db.scalar(
        select(Milestone)
        .where(
            Milestone.project_id == project_id,
            Milestone.name == milestone_name,
        )
    )

    if milestone is None:
        raise ValueError("Milestone not found.")

    result = await db.scalars(
        select(Ticket)
        .where(
            Ticket.project_id == project_id,
            Ticket.milestone_id == milestone.id,
        )
    )

    tickets = result.all()

    if not tickets:
        return MilestoneProgressResponse(
            success=True,
            status_code=status.HTTP_200_OK,
            message="No tickets found for this milestone.",
            data=[],
        )

    total_tickets = len(tickets)

    # ---------------------------------------------------------
    # Build the timeline.
    #
    # Start dates and end dates are included so the frontend
    # gets points covering the complete milestone timeline.
    # ---------------------------------------------------------

    dates: set[datetime] = set()

    for ticket in tickets:

        if ticket.expected_start_date is not None:
            dates.add(ticket.expected_start_date)

        if ticket.expected_end_date is not None:
            dates.add(ticket.expected_end_date)

        if ticket.actual_start_date is not None:
            dates.add(ticket.actual_start_date)

        if ticket.actual_end_date is not None:
            dates.add(ticket.actual_end_date)

    now = datetime.now(timezone.utc)

    dates.add(now)

    progress_points: list[MilestoneProgressPoint] = []

    for graph_date in sorted(dates):

        expected_completed = 0
        actual_completed = 0

        for ticket in tickets:

            # -------------------------------------------------
            # EXPECTED
            #
            # A ticket contributes to expected completion when
            # its expected end date has been reached.
            # -------------------------------------------------

            if (
                ticket.expected_end_date is not None
                and ticket.expected_end_date <= graph_date
            ):
                expected_completed += 1

            # -------------------------------------------------
            # ACTUAL
            #
            # A ticket is considered actually completed ONLY
            # when it has an actual end date.
            # -------------------------------------------------

            if (
                ticket.actual_end_date is not None
                and ticket.actual_end_date <= graph_date
            ):
                actual_completed += 1

        expected_percentage = (
            expected_completed / total_tickets
        ) * 100

        actual_percentage = (
            actual_completed / total_tickets
        ) * 100

        progress_points.append(
            MilestoneProgressPoint(
                date=graph_date,
                expected_percentage=round(
                    expected_percentage,
                    2,
                ),
                actual_percentage=round(
                    actual_percentage,
                    2,
                ),
            )
        )

    return MilestoneProgressResponse(
        success=True,
        status_code=status.HTTP_200_OK,
        message="Milestone progress retrieved successfully.",
        data=progress_points,
    )
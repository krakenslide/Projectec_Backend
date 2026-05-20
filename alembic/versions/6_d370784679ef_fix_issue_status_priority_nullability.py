"""fix issue status priority nullability

Revision ID: d370784679ef
Revises: 34a85ce60cac
Create Date: 2026-05-17 18:41:51.682329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd370784679ef'
down_revision: Union[str, Sequence[str], None] = '34a85ce60cac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        UPDATE app.issues
        SET status = 'TODO'
        WHERE status IS NULL
    """)

    op.execute("""
        UPDATE app.issues
        SET priority = 'MEDIUM'
        WHERE priority IS NULL
    """)

    op.alter_column(
        "issues",
        "status",
        existing_type=sa.String(),
        nullable=False,
        schema="app",
    )

    op.alter_column(
        "issues",
        "priority",
        existing_type=sa.String(),
        nullable=False,
        schema="app",
    )


def downgrade() -> None:
    op.alter_column(
        "issues",
        "priority",
        existing_type=sa.String(),
        nullable=True,
        schema="app",
    )

    op.alter_column(
        "issues",
        "status",
        existing_type=sa.String(),
        nullable=True,
        schema="app",
    )
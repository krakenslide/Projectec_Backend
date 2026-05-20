"""make issue position non nullable

Revision ID: 144b0248da21
Revises: 6b54da338597
Create Date: 2026-05-17 18:22:11.983443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '144b0248da21'
down_revision: Union[str, Sequence[str], None] = '6b54da338597'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Backfill existing NULL positions
    op.execute("""
        UPDATE app.issues
        SET position = 0
        WHERE position IS NULL
    """)

    # 2. Make column NOT NULL
    op.alter_column(
        "issues",
        "position",
        existing_type=sa.Integer(),
        nullable=False,
        schema="app",
    )


def downgrade() -> None:
    op.alter_column(
        "issues",
        "position",
        existing_type=sa.Integer(),
        nullable=True,
        schema="app",
    )
"""Added code column in project

Revision ID: 89110e0e1e0f
Revises: 077cd6f009c2
Create Date: 2026-07-29 14:09:54.330373

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "89110e0e1e0f"
down_revision: Union[str, Sequence[str], None] = "077cd6f009c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "project", sa.Column("code", sa.String(length=10), nullable=True), schema="app"
    )


def downgrade() -> None:
    op.drop_column("project", "code", schema="app")

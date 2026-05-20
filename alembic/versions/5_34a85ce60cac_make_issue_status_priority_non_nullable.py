"""make issue status priority non nullable

Revision ID: 34a85ce60cac
Revises: 144b0248da21
Create Date: 2026-05-17 18:38:05.425737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34a85ce60cac'
down_revision: Union[str, Sequence[str], None] = '144b0248da21'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

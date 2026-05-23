"""add email verification

Revision ID: 3574b8fbde73
Revises: b5c7a15341f4
Create Date: 2026-05-23 11:40:03.672366

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '3574b8fbde73'
down_revision: Union[str, Sequence[str], None] = 'b5c7a15341f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), server_default=sa.false()), schema='app')
    op.add_column('users', sa.Column('verification_token', sa.String(),nullable=True ), schema='app')
    op.alter_column(
        'users',
        'password_hash',
        existing_type=sa.String(),
        nullable=True,
        schema='app'
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_verified', schema='app')
    op.drop_column('users', 'verification_token', schema='app')
    op.alter_column(
        'users',
        'password_hash',
        existing_type=sa.String(),
        nullable=False,
        schema='app'
    )

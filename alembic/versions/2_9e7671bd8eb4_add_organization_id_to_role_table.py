"""Add organization_id to role table

Revision ID: 9e7671bd8eb4
Revises: 3694d65cdeb5
Create Date: 2026-06-28 13:07:34.853987

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '9e7671bd8eb4'
down_revision: Union[str, Sequence[str], None] = '3694d65cdeb5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('role', sa.Column('organization_id', sa.UUID(), nullable=False), schema='app')
    op.create_foreign_key("fk_role_organization", 'role', 'organization', ['organization_id'], ['id'], source_schema='app', referent_schema='app')
    op.create_unique_constraint(
        "uq_role_organization_name",
        "role",
        ["organization_id", "name"],
        schema="app",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_role_organization_name",
        "role",
        schema="app",
        type_="unique",
    )
    op.drop_constraint("fk_role_organization", 'role', schema='app', type_='foreignkey')
    op.drop_column('role', 'organization_id', schema='app')
    # ### end Alembic commands ###

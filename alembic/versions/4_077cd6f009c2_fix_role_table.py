"""Fix role table

Revision ID: 077cd6f009c2
Revises: 5e384d56a098
Create Date: 2026-07-19 22:10:17.666039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '077cd6f009c2'
down_revision: Union[str, Sequence[str], None] = '5e384d56a098'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


role_type_enum = sa.Enum(
    "ORGANIZATION",
    "PROJECT",
    name="roletype",
    native_enum=False,
)


def upgrade():
    role_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "role",
        sa.Column(
            "role_type",
            role_type_enum,
            nullable=True,
        ),
        schema="app",
    )

    op.alter_column(
        "role",
        "role_type",
        nullable=False,
        schema="app",
    )

    op.drop_column(
        "role",
        "organization_id",
        schema="app",
    )


def downgrade():

    op.add_column(
        "role",
        sa.Column(
            "organization_id",
            sa.UUID(),
            nullable=True,
        ),
        schema="app",
    )

    op.drop_column(
        "role",
        "role_type",
        schema="app",
    )
    role_type_enum.drop(op.get_bind(), checkfirst=True)

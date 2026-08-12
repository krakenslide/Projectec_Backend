"""add milestones and milestone to tickets

Revision ID: fd86818df929
Revises: 6bb822c09e2d
Create Date: 2026-08-12 02:02:23.275356

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.core.config import DB_SCHEMA

# revision identifiers, used by Alembic.
revision: str = 'fd86818df929'
down_revision: Union[str, Sequence[str], None] = '6bb822c09e2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "milestone",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.Column(
            "updated_by",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{DB_SCHEMA}.project.id"],
        ),

        sa.PrimaryKeyConstraint("id"),

        schema=DB_SCHEMA,
    )

    op.create_index(
        "ix_milestone_project_id",
        "milestone",
        ["project_id"],
        unique=False,
        schema=DB_SCHEMA,
    )

    op.add_column(
        "ticket",
        sa.Column(
            "milestone_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
        schema=DB_SCHEMA,
    )

    op.create_index(
        "ix_ticket_milestone_id",
        "ticket",
        ["milestone_id"],
        unique=False,
        schema=DB_SCHEMA,
    )

    op.create_foreign_key(
        "fk_ticket_milestone_id",
        "ticket",
        "milestone",
        ["milestone_id"],
        ["id"],
        source_schema=DB_SCHEMA,
        referent_schema=DB_SCHEMA,
    )


def downgrade() -> None:

    op.drop_constraint(
        "fk_ticket_milestone_id",
        "ticket",
        schema=DB_SCHEMA,
        type_="foreignkey",
    )

    op.drop_index(
        "ix_ticket_milestone_id",
        table_name="ticket",
        schema=DB_SCHEMA,
    )

    op.drop_column(
        "ticket",
        "milestone_id",
        schema=DB_SCHEMA,
    )

    op.drop_index(
        "ix_milestone_project_id",
        table_name="milestone",
        schema=DB_SCHEMA,
    )

    op.drop_table(
        "milestone",
        schema=DB_SCHEMA,
    )
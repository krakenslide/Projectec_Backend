"""Added User Project Table

Revision ID: 5e384d56a098
Revises: 9e7671bd8eb4
Create Date: 2026-07-16 10:45:12.884217

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app.core.config import DB_SCHEMA
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "5e384d56a098"
down_revision: Union[str, Sequence[str], None] = "9e7671bd8eb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_project",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        # AuditMixin columns
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
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{DB_SCHEMA}.project.id"],
            name="fk_user_project_project_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            [f"{DB_SCHEMA}.user.id"],
            name="fk_user_project_user_id",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            [f"{DB_SCHEMA}.role.id"],
            name="fk_user_project_role_id",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_user_project"),
        schema=DB_SCHEMA,
    )

    op.create_index(
        "ix_user_project_project_id",
        "user_project",
        ["project_id"],
        unique=False,
        schema=DB_SCHEMA,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_user_project_project_id",
        table_name="user_project",
        schema=DB_SCHEMA,
    )

    op.drop_table(
        "user_project",
        schema=DB_SCHEMA,
    )

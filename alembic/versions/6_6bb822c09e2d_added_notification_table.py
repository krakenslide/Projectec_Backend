"""Added notification table

Revision ID: 6bb822c09e2d
Revises: 89110e0e1e0f
Create Date: 2026-08-02 12:08:15.775883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6bb822c09e2d'
down_revision: Union[str, Sequence[str], None] = '89110e0e1e0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():

    op.create_table(
        "notification",

        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "project_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.Column(
            "ticket_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.Column(
            "recipient_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "actor_user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.Column(
            "notification_type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "message",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "action_url",
            sa.String(length=500),
            nullable=True,
        ),

        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),

        sa.Column(
            "is_read",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),

        # AuditMixin columns
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
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

        sa.PrimaryKeyConstraint("id"),

        sa.ForeignKeyConstraint(
            ["organization_id"],
            [f"{'app'}.organization.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["project_id"],
            [f"{'app'}.project.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["ticket_id"],
            [f"{'app'}.ticket.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["recipient_user_id"],
            [f"{'app'}.user.id"],
            ondelete="CASCADE",
        ),

        sa.ForeignKeyConstraint(
            ["actor_user_id"],
            [f"{'app'}.user.id"],
            ondelete="SET NULL",
        ),

        schema='app',
    )

    op.create_index(
        "ix_notification_organization_id",
        "notification",
        ["organization_id"],
        unique=False,
        schema='app',
    )

    op.create_index(
        "ix_notification_project_id",
        "notification",
        ["project_id"],
        unique=False,
        schema='app',
    )

    op.create_index(
        "ix_notification_ticket_id",
        "notification",
        ["ticket_id"],
        unique=False,
        schema='app',
    )

    op.create_index(
        "ix_notification_recipient_user_id",
        "notification",
        ["recipient_user_id"],
        unique=False,
        schema='app',
    )

    op.create_index(
        "ix_notification_actor_user_id",
        "notification",
        ["actor_user_id"],
        unique=False,
        schema='app',
    )

    op.create_index(
        "ix_notification_is_read",
        "notification",
        ["is_read"],
        unique=False,
        schema='app',
    )


def downgrade():

    op.drop_index(
        "ix_notification_is_read",
        table_name="notification",
        schema='app',
    )

    op.drop_index(
        "ix_notification_actor_user_id",
        table_name="notification",
        schema='app',
    )

    op.drop_index(
        "ix_notification_recipient_user_id",
        table_name="notification",
        schema='app',
    )

    op.drop_index(
        "ix_notification_ticket_id",
        table_name="notification",
        schema='app',
    )

    op.drop_index(
        "ix_notification_project_id",
        table_name="notification",
        schema='app',
    )

    op.drop_index(
        "ix_notification_organization_id",
        table_name="notification",
        schema='app',
    )

    op.drop_table(
        "notification",
        schema='app',
    )

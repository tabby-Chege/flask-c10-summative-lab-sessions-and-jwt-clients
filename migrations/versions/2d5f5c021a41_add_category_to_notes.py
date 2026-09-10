"""Add category to notes

Revision ID: 2d5f5c021a41
Revises: 7c9c8fd9d2b1
Create Date: 2026-09-10 19:05:23.087481

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2d5f5c021a41"
down_revision = "7c9c8fd9d2b1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("notes", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "category",
                sa.String(length=50),
                nullable=False,
                server_default="general",
            )
        )

    with op.batch_alter_table("notes", schema=None) as batch_op:
        batch_op.alter_column(
            "category",
            server_default=None,
        )


def downgrade():
    with op.batch_alter_table("notes", schema=None) as batch_op:
        batch_op.drop_column("category")

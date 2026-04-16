"""add is_saved to properties

Revision ID: 002
Revises: 001
Create Date: 2026-04-15
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "properties",
        sa.Column("is_saved", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade():
    op.drop_column("properties", "is_saved")

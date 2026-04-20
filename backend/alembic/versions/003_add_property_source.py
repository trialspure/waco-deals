"""add source and listing_type to properties

Revision ID: 003
Revises: 002
Create Date: 2026-04-19
"""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "properties",
        sa.Column("source", sa.String(), nullable=False, server_default="zillow"),
    )
    op.add_column(
        "properties",
        sa.Column("listing_type", sa.String(), nullable=False, server_default="sale"),
    )
    op.create_index("ix_properties_source", "properties", ["source"])


def downgrade():
    op.drop_index("ix_properties_source", table_name="properties")
    op.drop_column("properties", "listing_type")
    op.drop_column("properties", "source")

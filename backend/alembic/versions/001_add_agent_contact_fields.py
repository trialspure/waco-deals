"""add agent contact fields

Revision ID: 001
Revises:
Create Date: 2026-04-15
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("properties", sa.Column("agent_name", sa.String(), nullable=True))
    op.add_column("properties", sa.Column("agent_email", sa.String(), nullable=True))
    op.add_column("properties", sa.Column("agent_phone", sa.String(), nullable=True))
    op.add_column("properties", sa.Column("brokerage", sa.String(), nullable=True))


def downgrade():
    op.drop_column("properties", "brokerage")
    op.drop_column("properties", "agent_phone")
    op.drop_column("properties", "agent_email")
    op.drop_column("properties", "agent_name")

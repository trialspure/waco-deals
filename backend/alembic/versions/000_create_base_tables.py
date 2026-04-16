"""create base tables

Revision ID: 000
Revises:
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "properties",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("zpid", sa.String(), unique=True, index=True),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("city", sa.String()),
        sa.Column("state", sa.String()),
        sa.Column("zip_code", sa.String(), index=True),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("beds", sa.Float()),
        sa.Column("baths", sa.Float()),
        sa.Column("sqft", sa.Float()),
        sa.Column("lot_size", sa.Float()),
        sa.Column("year_built", sa.Integer()),
        sa.Column("property_type", sa.String()),
        sa.Column("asking_price", sa.Float()),
        sa.Column("zestimate", sa.Float()),
        sa.Column("price_per_sqft", sa.Float()),
        sa.Column("days_on_market", sa.Integer()),
        sa.Column("estimated_rent", sa.Float()),
        sa.Column("rent_fetched_at", sa.DateTime()),
        sa.Column("listing_url", sa.String()),
        sa.Column("photo_url", sa.String()),
        sa.Column("description", sa.Text()),
        sa.Column("status", sa.String()),
        sa.Column("scraped_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )

    op.create_table(
        "scores",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id"), unique=True, nullable=False),
        sa.Column("wholesale_score", sa.Float()),
        sa.Column("wholesale_equity_pct", sa.Float()),
        sa.Column("wholesale_max_offer", sa.Float()),
        sa.Column("wholesale_est_repairs", sa.Float()),
        sa.Column("flip_score", sa.Float()),
        sa.Column("flip_profit", sa.Float()),
        sa.Column("flip_margin_pct", sa.Float()),
        sa.Column("flip_max_offer", sa.Float()),
        sa.Column("rental_score", sa.Float()),
        sa.Column("rental_cap_rate", sa.Float()),
        sa.Column("rental_monthly_rent", sa.Float()),
        sa.Column("rental_annual_cashflow", sa.Float()),
        sa.Column("airbnb_score", sa.Float()),
        sa.Column("airbnb_nightly_rate", sa.Float()),
        sa.Column("airbnb_monthly_revenue", sa.Float()),
        sa.Column("airbnb_annual_yield", sa.Float()),
        sa.Column("best_strategy", sa.String()),
        sa.Column("best_score", sa.Float()),
        sa.Column("scored_at", sa.DateTime()),
    )

    op.create_table(
        "offer_letters",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("property_id", sa.Integer(), sa.ForeignKey("properties.id"), nullable=False),
        sa.Column("buyer_name", sa.String(), nullable=False),
        sa.Column("buyer_address", sa.String()),
        sa.Column("buyer_phone", sa.String()),
        sa.Column("buyer_email", sa.String()),
        sa.Column("strategy", sa.String(), nullable=False),
        sa.Column("offer_price", sa.Float(), nullable=False),
        sa.Column("earnest_money", sa.Float()),
        sa.Column("closing_days", sa.Integer()),
        sa.Column("inspection_days", sa.Integer()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime()),
    )

    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("key", sa.String(), unique=True, nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime()),
    )


def downgrade():
    op.drop_table("offer_letters")
    op.drop_table("scores")
    op.drop_table("app_settings")
    op.drop_table("properties")

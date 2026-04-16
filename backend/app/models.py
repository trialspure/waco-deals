from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from app.database import Base


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    zpid = Column(String, unique=True, index=True)  # Zillow property ID

    # Location
    address = Column(String, nullable=False)
    city = Column(String, default="Waco")
    state = Column(String, default="TX")
    zip_code = Column(String, index=True)
    latitude = Column(Float)
    longitude = Column(Float)

    # Property details
    beds = Column(Float)
    baths = Column(Float)
    sqft = Column(Float)
    lot_size = Column(Float)
    year_built = Column(Integer)
    property_type = Column(String)

    # Pricing
    asking_price = Column(Float)
    zestimate = Column(Float)
    price_per_sqft = Column(Float)
    days_on_market = Column(Integer)

    # Rental data (from RentCast)
    estimated_rent = Column(Float)
    rent_fetched_at = Column(DateTime)

    # Agent / seller contact
    agent_name = Column(String)
    agent_email = Column(String)
    agent_phone = Column(String)
    brokerage = Column(String)

    # User actions
    is_saved = Column(Boolean, default=False)

    # Listing metadata
    listing_url = Column(String)
    photo_url = Column(String)
    description = Column(Text)
    status = Column(String, default="FOR_SALE")

    scraped_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scores = relationship("Score", back_populates="property", uselist=False, cascade="all, delete-orphan")
    offers = relationship("OfferLetter", back_populates="property", cascade="all, delete-orphan")


class Score(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), unique=True, nullable=False)

    # Wholesale
    wholesale_score = Column(Float)
    wholesale_equity_pct = Column(Float)
    wholesale_max_offer = Column(Float)
    wholesale_est_repairs = Column(Float)

    # Fix & Flip
    flip_score = Column(Float)
    flip_profit = Column(Float)
    flip_margin_pct = Column(Float)
    flip_max_offer = Column(Float)

    # Long-term rental
    rental_score = Column(Float)
    rental_cap_rate = Column(Float)
    rental_monthly_rent = Column(Float)
    rental_annual_cashflow = Column(Float)

    # Airbnb / STR
    airbnb_score = Column(Float)
    airbnb_nightly_rate = Column(Float)
    airbnb_monthly_revenue = Column(Float)
    airbnb_annual_yield = Column(Float)

    # Best strategy
    best_strategy = Column(String)  # "wholesale" | "flip" | "rental" | "airbnb"
    best_score = Column(Float)

    scored_at = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="scores")


class OfferLetter(Base):
    __tablename__ = "offer_letters"

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)

    buyer_name = Column(String, nullable=False)
    buyer_address = Column(String)
    buyer_phone = Column(String)
    buyer_email = Column(String)

    strategy = Column(String, nullable=False)
    offer_price = Column(Float, nullable=False)
    earnest_money = Column(Float, default=1000.0)
    closing_days = Column(Integer, default=21)
    inspection_days = Column(Integer, default=10)
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    property = relationship("Property", back_populates="offers")


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

"""Shared helpers for property scrapers (Zillow, Facebook Marketplace, ...).

Dedup key is the namespaced `zpid` column — populated with real zpids for Zillow,
"fb_<post_id>" for Facebook Marketplace, or "addr_<md5>" as a last-resort fallback.
"""
from sqlalchemy.orm import Session
from app.models import Property


def upsert_property(db: Session, data: dict) -> Property:
    """Insert or update a Property row, matching on the namespaced zpid."""
    prop = db.query(Property).filter(Property.zpid == data["zpid"]).first()
    if prop:
        for k, v in data.items():
            if v is not None:
                setattr(prop, k, v)
    else:
        prop = Property(**data)
        db.add(prop)
    db.commit()
    db.refresh(prop)
    return prop

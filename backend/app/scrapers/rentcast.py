"""
RentCast API integration.
Fetches rent estimates for properties stored in the DB.
"""
import httpx
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Property

logger = logging.getLogger(__name__)

RENTCAST_BASE = "https://api.rentcast.io/v1"


def fetch_rent_estimate(address: str, zip_code: str, beds: float, baths: float, sqft: float) -> float | None:
    """Call RentCast rent estimate endpoint. Returns monthly rent or None."""
    if not settings.rentcast_api_key or settings.rentcast_api_key == "your_rentcast_key_here":
        return None

    headers = {"X-Api-Key": settings.rentcast_api_key}
    params = {
        "address": address,
        "zipCode": zip_code,
        "bedrooms": int(beds) if beds else 3,
        "bathrooms": float(baths) if baths else 2,
        "squareFootage": int(sqft) if sqft else 1200,
        "propertyType": "Single Family",
    }
    try:
        resp = httpx.get(f"{RENTCAST_BASE}/avm/rent/long-term", headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rent = data.get("rent") or data.get("rentRangeLow")
        return float(rent) if rent else None
    except httpx.HTTPStatusError as e:
        logger.warning(f"RentCast HTTP error for {address}: {e.response.status_code}")
        return None
    except Exception as e:
        logger.warning(f"RentCast error for {address}: {e}")
        return None


def enrich_properties_with_rent(db: Session) -> int:
    """
    For all properties without a rent estimate, fetch from RentCast.
    Returns count of properties updated.
    """
    props = db.query(Property).filter(Property.estimated_rent == None).all()  # noqa: E711
    updated = 0
    for prop in props:
        sqft = prop.sqft or 1200
        rent = fetch_rent_estimate(
            address=prop.address,
            zip_code=prop.zip_code or "76701",
            beds=prop.beds or 3,
            baths=prop.baths or 2,
            sqft=sqft,
        )
        if rent is None:
            # Fallback: sqft × rent_per_sqft_fallback
            rent = sqft * settings.rent_per_sqft_fallback

        prop.estimated_rent = rent
        prop.rent_fetched_at = datetime.utcnow()
        updated += 1

    db.commit()
    logger.info(f"RentCast enrichment complete — {updated} properties updated")
    return updated

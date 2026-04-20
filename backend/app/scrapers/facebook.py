"""Facebook Marketplace scraper via RapidAPI.

FB Marketplace is not officially scrape-able, so we use a third-party RapidAPI
provider that handles login sessions and anti-bot on our behalf. Both the paid
provider host and the API key come from config — if the provider changes, only
the parsing in _parse_property needs to be re-tuned.

Default provider slug: "facebook-marketplace-api" (user selects actual provider
on RapidAPI marketplace and sets FB_MARKETPLACE_RAPIDAPI_KEY). See README.

Scrapes two categories per run:
- "propertyforsale" — FSBO homes (treated as source='facebook_marketplace', listing_type='sale')
- "propertyrentals" — landlord rental posts (acquisition targets, listing_type='rent', no sale price)

Waco is filtered by lat/lon + radius (FB's search API uses a location + radius
rather than a bounding box).
"""
import logging
from datetime import datetime
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Property
from app.scrapers._common import upsert_property

logger = logging.getLogger(__name__)

RAPIDAPI_HOST = "facebook-marketplace-api.p.rapidapi.com"

# Waco city center + radius (km). FB Marketplace search APIs typically accept
# a location/radius pair rather than a bbox. Radius chosen to roughly cover
# 76701-76712 ZIP codes.
WACO_LAT = 31.5493
WACO_LON = -97.1467
WACO_RADIUS_KM = 25

MAX_PAGES = 5  # conservative — paid FB scraper APIs tend to rate-limit hard

# FB Marketplace category slugs — these vary by provider; adjust to match chosen API.
CATEGORY_FOR_SALE = "propertyforsale"
CATEGORY_RENTALS = "propertyrentals"


def _headers() -> dict:
    # Some providers share an account with other RapidAPI subscriptions, so
    # fall back to the main rapidapi_key if the FB-specific key is not set.
    key = settings.fb_marketplace_rapidapi_key or settings.rapidapi_key
    return {
        "x-rapidapi-key": key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }


def _search_listings(category: str, page: int = 1) -> dict:
    """Call the RapidAPI search endpoint for a given category + page."""
    url = f"https://{RAPIDAPI_HOST}/search"
    params = {
        "category": category,
        "latitude": str(WACO_LAT),
        "longitude": str(WACO_LON),
        "radius": str(WACO_RADIUS_KM),
        "page": str(page),
    }
    resp = httpx.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _make_fb_id(raw: dict) -> str:
    post_id = raw.get("id") or raw.get("post_id") or raw.get("listing_id")
    if not post_id:
        return ""
    return f"fb_{post_id}"


def _parse_price(val) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "").replace("$", "").strip())
    except (ValueError, TypeError):
        return None


def _parse_property(raw: dict, listing_type: str) -> Optional[dict]:
    """Normalize a raw FB Marketplace listing into our Property schema shape.

    For `listing_type == "sale"`: price goes into asking_price.
    For `listing_type == "rent"`: the posted price is a monthly rent — store it
    in estimated_rent instead and leave asking_price null, so the scoring
    engine skips it (rentals become "acquisition targets").
    """
    zpid = _make_fb_id(raw)
    if not zpid:
        return None

    price = _parse_price(raw.get("price") or raw.get("amount"))
    if price is None:
        return None

    # Location — FB Marketplace formats vary by provider; check common shapes.
    loc = raw.get("location") or {}
    street = (
        raw.get("address")
        or loc.get("address")
        or raw.get("title")  # Fallback: "3 bed house on Main St" is better than nothing
        or "Unknown"
    )
    city = loc.get("city") or raw.get("city") or "Waco"
    state = loc.get("state") or raw.get("state") or "TX"
    zip_code_val = loc.get("zip") or loc.get("postal_code") or raw.get("zip") or ""
    latitude = loc.get("latitude") or raw.get("latitude")
    longitude = loc.get("longitude") or raw.get("longitude")

    beds = raw.get("bedrooms") or raw.get("beds")
    baths = raw.get("bathrooms") or raw.get("baths")
    sqft = raw.get("sqft") or raw.get("area")
    try:
        sqft = float(str(sqft).replace(",", "")) if sqft else None
    except (ValueError, TypeError):
        sqft = None

    # Marketplace listing URL — click-through target for the user.
    listing_url = raw.get("url") or raw.get("listing_url")
    if listing_url and not listing_url.startswith("http"):
        listing_url = "https://www.facebook.com" + listing_url

    photos = raw.get("photos") or raw.get("images") or []
    photo_url = None
    if isinstance(photos, list) and photos:
        first = photos[0]
        photo_url = first if isinstance(first, str) else (first.get("url") if isinstance(first, dict) else None)
    if not photo_url:
        photo_url = raw.get("photo_url") or raw.get("image_url")

    seller_name = raw.get("seller_name") or (raw.get("seller") or {}).get("name")

    base = {
        "zpid": zpid,
        "address": street,
        "city": city,
        "state": state,
        "zip_code": str(zip_code_val) if zip_code_val else "",
        "latitude": latitude,
        "longitude": longitude,
        "beds": beds,
        "baths": baths,
        "sqft": sqft,
        "property_type": raw.get("property_type") or "SINGLE_FAMILY",
        "listing_url": listing_url,
        "photo_url": photo_url,
        "description": raw.get("description") or raw.get("title") or "",
        # Seller appears in the agent_name field so the existing UI just works.
        "agent_name": seller_name,
        "source": "facebook_marketplace",
        "listing_type": listing_type,
    }

    if listing_type == "sale":
        base["asking_price"] = price
        base["status"] = "FOR_SALE"
        base["price_per_sqft"] = (price / sqft) if sqft else None
    else:
        # Rental: the posted price is monthly rent, not a sale price.
        base["estimated_rent"] = price
        base["rent_fetched_at"] = datetime.utcnow()
        base["status"] = "FOR_RENT"
        # asking_price intentionally left absent — scoring engine will skip this row.

    return base


def _scrape_category(db: Session, category: str, listing_type: str) -> int:
    total = 0
    try:
        for page in range(1, MAX_PAGES + 1):
            data = _search_listings(category, page)

            # Response shape varies by provider. Try common keys.
            if isinstance(data, dict):
                listings = (
                    data.get("listings")
                    or data.get("results")
                    or (data.get("data") or {}).get("listings")
                    or []
                )
            elif isinstance(data, list):
                listings = data
            else:
                listings = []

            if not listings:
                logger.info(f"FB {category} page {page}: no listings — stopping")
                break

            saved = 0
            for raw in listings:
                if not isinstance(raw, dict):
                    continue
                parsed = _parse_property(raw, listing_type)
                if parsed:
                    upsert_property(db, parsed)
                    total += 1
                    saved += 1

            logger.info(f"FB {category} page {page}: {len(listings)} listings, {saved} saved")

            if len(listings) < 20:
                break
    except httpx.HTTPStatusError as e:
        logger.error(f"FB {category} HTTP error: {e.response.status_code} — {e.response.text[:400]}")
        if e.response.status_code in (403, 429):
            logger.error("FB Marketplace RapidAPI quota hit — stopping category")
    except Exception as e:
        logger.error(f"FB {category} scrape error: {e}")

    return total


def scrape_facebook_listings(db: Session) -> int:
    """Scrape FB Marketplace FSBO + rentals in the Waco area.

    Returns total number of rows saved/updated.
    """
    key = settings.fb_marketplace_rapidapi_key or settings.rapidapi_key
    if not key or key == "your_fb_marketplace_rapidapi_key_here":
        logger.warning("FB_MARKETPLACE_RAPIDAPI_KEY not set — skipping FB scrape")
        return 0

    total = 0
    total += _scrape_category(db, CATEGORY_FOR_SALE, "sale")
    total += _scrape_category(db, CATEGORY_RENTALS, "rent")
    logger.info(f"FB Marketplace scrape complete — {total} properties processed")
    return total

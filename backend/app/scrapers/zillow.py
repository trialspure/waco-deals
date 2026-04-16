"""
Zillow property scraper via RapidAPI (zillow-com1.p.rapidapi.com).
Fetches active for-sale listings in Waco, TX ZIP codes.
"""
import hashlib
import httpx
import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.models import Property

logger = logging.getLogger(__name__)

RAPIDAPI_HOST = "real-estate-zillow-com.p.rapidapi.com"

# Bounding box covering all Waco, TX ZIP codes (76701–76712)
WACO_BBOX = {
    "north": 31.640,
    "south": 31.460,
    "east": -97.030,
    "west": -97.320,
}
MAX_PAGES = 10  # conservative — free tier has limited requests/month


def _headers() -> dict:
    return {
        "x-rapidapi-key": settings.rapidapi_key,
        "x-rapidapi-host": RAPIDAPI_HOST,
    }


def _search_listings(page: int = 1) -> dict:
    url = f"https://{RAPIDAPI_HOST}/v1/search/coords"
    params = {
        "type": "sale",
        "north": str(WACO_BBOX["north"]),
        "south": str(WACO_BBOX["south"]),
        "east": str(WACO_BBOX["east"]),
        "west": str(WACO_BBOX["west"]),
        "page": str(page),
    }
    resp = httpx.get(url, headers=_headers(), params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def _make_zpid(raw: dict) -> str:
    zpid = raw.get("zpid") or raw.get("id")
    if zpid and str(zpid) not in ("0", "None", "null", ""):
        return str(zpid)
    address = str(raw.get("address") or "")
    if address:
        return "addr_" + hashlib.md5(address.encode()).hexdigest()[:12]
    return ""


def _parse_price(val) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(str(val).replace(",", "").replace("$", "").strip())
    except (ValueError, TypeError):
        return None


def _parse_property(raw: dict) -> Optional[dict]:
    """Normalize a raw real-estate-zillow-com listing into our schema."""
    zpid = _make_zpid(raw)
    if not zpid:
        return None

    asking = _parse_price(raw.get("unformattedPrice") or raw.get("price"))
    zestimate = _parse_price(raw.get("zestimate")) or asking

    if not asking:
        return None

    # Detailed info lives inside hdpData.homeInfo
    home_info = (raw.get("hdpData") or {}).get("homeInfo") or {}

    sqft = raw.get("area") or home_info.get("livingArea")
    try:
        sqft = float(str(sqft).replace(",", "")) if sqft else None
    except (ValueError, TypeError):
        sqft = None

    # Flat address fields on this API
    street = raw.get("addressStreet") or home_info.get("streetAddress") or "Unknown"
    city = raw.get("addressCity") or home_info.get("city") or "Waco"
    state = raw.get("addressState") or home_info.get("state") or "TX"
    zip_code_val = raw.get("addressZipcode") or home_info.get("zipcode") or ""

    # Coordinates nested under latLong
    lat_long = raw.get("latLong") or {}
    latitude = lat_long.get("latitude") or home_info.get("latitude")
    longitude = lat_long.get("longitude") or home_info.get("longitude")

    listing_url = raw.get("detailUrl") or f"https://www.zillow.com/homes/{zpid}_zpid/"
    if listing_url and not listing_url.startswith("http"):
        listing_url = "https://www.zillow.com" + listing_url

    return {
        "zpid": zpid,
        "address": street,
        "city": city,
        "state": state,
        "zip_code": zip_code_val,
        "latitude": latitude,
        "longitude": longitude,
        "beds": raw.get("beds") or home_info.get("bedrooms"),
        "baths": raw.get("baths") or home_info.get("bathrooms"),
        "sqft": sqft,
        "lot_size": home_info.get("lotAreaValue"),
        "year_built": home_info.get("yearBuilt"),
        "property_type": home_info.get("homeType") or "SINGLE_FAMILY",
        "asking_price": asking,
        "zestimate": zestimate,
        "price_per_sqft": (asking / sqft) if asking and sqft else None,
        "days_on_market": home_info.get("daysOnZillow"),
        "listing_url": listing_url,
        "photo_url": raw.get("imgSrc"),
        "description": raw.get("description") or "",
        "status": "FOR_SALE",
    }


def upsert_property(db: Session, data: dict) -> Property:
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


def scrape_waco_listings(db: Session) -> int:
    """
    Scrape Waco area via RapidAPI real-estate-zillow-com bounding box search, upsert to DB.
    Returns count of properties saved/updated.
    """
    if not settings.rapidapi_key or settings.rapidapi_key == "your_rapidapi_key_here":
        logger.warning("RAPIDAPI_KEY not set — skipping scrape")
        return 0

    total = 0
    _logged_sample = False

    try:
        for page in range(1, MAX_PAGES + 1):
            data = _search_listings(page)

            # Response shape: {"data": {"url": "...", "listings": [...], "count": N, ...}}
            inner = data.get("data") if isinstance(data, dict) else None
            if isinstance(inner, dict):
                listings = inner.get("listings") or inner.get("props") or inner.get("results") or []
            elif isinstance(data, list) and len(data) >= 2 and isinstance(data[1], list):
                listings = data[1]
            elif isinstance(data, dict):
                listings = (
                    data.get("listings") or data.get("props")
                    or data.get("results") or []
                )
            else:
                listings = []

            if not listings:
                logger.info(f"Page {page}: no listings returned — stopping")
                break

            if not _logged_sample:
                logger.info(f"Page {page}: {len(listings)} listings received")
                _logged_sample = True

            saved = 0
            for raw in listings:
                if not isinstance(raw, dict):
                    continue
                parsed = _parse_property(raw)
                if parsed:
                    upsert_property(db, parsed)
                    total += 1
                    saved += 1

            logger.info(f"Page {page}: {len(listings)} listings, {saved} saved")

            # If fewer than expected results, no more pages
            if len(listings) < 20:
                break

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error: {e.response.status_code} — {e.response.text[:400]}")
        if e.response.status_code in (403, 429):
            logger.error("RapidAPI quota hit — stopping scrape")
    except Exception as e:
        logger.error(f"Scrape error: {e}")

    logger.info(f"RapidAPI scrape complete — {total} properties processed")
    return total

"""
Run this to insert sample Waco properties for testing the UI.
Usage: py -3.12 seed.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import Base, Property
from app.scoring.engine import score_all_properties
from app.scrapers.rentcast import enrich_properties_with_rent

Base.metadata.create_all(bind=engine)

SAMPLE_PROPERTIES = [
    {
        "zpid": "test_001",
        "address": "1823 Speight Ave",
        "city": "Waco", "state": "TX", "zip_code": "76706",
        "latitude": 31.5391, "longitude": -97.1328,
        "beds": 3, "baths": 1, "sqft": 1100, "year_built": 1948,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 79900, "zestimate": 135000,
        "days_on_market": 14,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "Older home near Baylor, needs full rehab.",
        "status": "FOR_SALE",
    },
    {
        "zpid": "test_002",
        "address": "412 N 15th St",
        "city": "Waco", "state": "TX", "zip_code": "76707",
        "latitude": 31.5512, "longitude": -97.1456,
        "beds": 4, "baths": 2, "sqft": 1800, "year_built": 1962,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 115000, "zestimate": 178000,
        "days_on_market": 5,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "Spacious 4/2 near downtown, cosmetic updates needed.",
        "status": "FOR_SALE",
    },
    {
        "zpid": "test_003",
        "address": "3301 Colcord Ave",
        "city": "Waco", "state": "TX", "zip_code": "76707",
        "latitude": 31.5478, "longitude": -97.1512,
        "beds": 3, "baths": 2, "sqft": 1400, "year_built": 1975,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 145000, "zestimate": 162000,
        "days_on_market": 22,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "Move-in ready, good rental area.",
        "status": "FOR_SALE",
    },
    {
        "zpid": "test_004",
        "address": "701 Primrose Dr",
        "city": "Waco", "state": "TX", "zip_code": "76710",
        "latitude": 31.5221, "longitude": -97.1789,
        "beds": 4, "baths": 3, "sqft": 2400, "year_built": 1995,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 285000, "zestimate": 310000,
        "days_on_market": 8,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "Well-maintained family home in west Waco.",
        "status": "FOR_SALE",
    },
    {
        "zpid": "test_005",
        "address": "2218 Grim Ave",
        "city": "Waco", "state": "TX", "zip_code": "76706",
        "latitude": 31.5345, "longitude": -97.1267,
        "beds": 2, "baths": 1, "sqft": 900, "year_built": 1940,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 52000, "zestimate": 98000,
        "days_on_market": 45,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "Deep discount fixer — possible wholesale deal.",
        "status": "FOR_SALE",
    },
    {
        "zpid": "test_006",
        "address": "1504 Herring Ave",
        "city": "Waco", "state": "TX", "zip_code": "76708",
        "latitude": 31.5689, "longitude": -97.1534,
        "beds": 3, "baths": 1, "sqft": 1250, "year_built": 1958,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 95000, "zestimate": 140000,
        "days_on_market": 31,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "North Waco rental area, steady demand.",
        "status": "FOR_SALE",
    },
    {
        "zpid": "test_007",
        "address": "512 S University Parks Dr",
        "city": "Waco", "state": "TX", "zip_code": "76706",
        "latitude": 31.5412, "longitude": -97.1198,
        "beds": 3, "baths": 2, "sqft": 1350, "year_built": 1985,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 189000, "zestimate": 205000,
        "days_on_market": 3,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "Near Baylor campus — strong Airbnb demand during football season.",
        "status": "FOR_SALE",
    },
    {
        "zpid": "test_008",
        "address": "4200 Hillcrest Dr",
        "city": "Waco", "state": "TX", "zip_code": "76710",
        "latitude": 31.5198, "longitude": -97.1823,
        "beds": 5, "baths": 3, "sqft": 3100, "year_built": 2001,
        "property_type": "SINGLE_FAMILY",
        "asking_price": 375000, "zestimate": 395000,
        "days_on_market": 12,
        "listing_url": "https://www.zillow.com",
        "photo_url": None, "description": "Large executive home, west Waco suburbs.",
        "status": "FOR_SALE",
    },
]

def run():
    db = SessionLocal()
    try:
        inserted = 0
        for data in SAMPLE_PROPERTIES:
            exists = db.query(Property).filter(Property.zpid == data["zpid"]).first()
            if not exists:
                db.add(Property(**data))
                inserted += 1
        db.commit()
        print(f"Inserted {inserted} sample properties")

        print("Adding rent estimates...")
        enrich_properties_with_rent(db)

        print("Scoring properties...")
        scored = score_all_properties(db)
        print(f"Scored {scored} properties")
        print("Done! Open http://localhost:3000 to see them.")
    finally:
        db.close()

if __name__ == "__main__":
    run()

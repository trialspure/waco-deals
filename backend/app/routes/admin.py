import logging

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.scrapers.zillow import scrape_waco_listings
from app.scrapers.facebook import scrape_facebook_listings
from app.scrapers.rentcast import enrich_properties_with_rent
from app.scoring.engine import score_all_properties
from app.models import Property, Score

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


def _run_full_pipeline():
    db = SessionLocal()
    try:
        scrape_waco_listings(db)
        # A failure in the FB leg should not kill the Zillow leg or scoring.
        try:
            scrape_facebook_listings(db)
        except Exception as e:
            logger.error(f"FB Marketplace scrape failed (continuing): {e}")
        enrich_properties_with_rent(db)
        score_all_properties(db)
    finally:
        db.close()


@router.post("/scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(_run_full_pipeline)
    return {"status": "pipeline started", "message": "Scraping Waco listings in background"}


@router.post("/score")
def trigger_score(db: Session = Depends(get_db)):
    enrich_properties_with_rent(db)
    count = score_all_properties(db)
    return {"status": "ok", "scored": count}


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Property).count()
    scored = db.query(Score).count()
    by_strategy = {}
    for strategy in ["wholesale", "flip", "rental", "airbnb"]:
        by_strategy[strategy] = db.query(Score).filter(Score.best_strategy == strategy).count()
    return {"total_properties": total, "scored": scored, "by_strategy": by_strategy}

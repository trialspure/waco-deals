"""
APScheduler — runs the full scrape + score pipeline every 6 hours.
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.database import SessionLocal
from app.scrapers.zillow import scrape_waco_listings
from app.scrapers.rentcast import enrich_properties_with_rent
from app.scoring.engine import score_all_properties

logger = logging.getLogger(__name__)
scheduler = BackgroundScheduler()


def run_pipeline():
    logger.info("Pipeline started")
    db = SessionLocal()
    try:
        count = scrape_waco_listings(db)
        logger.info(f"Scraped {count} listings")
        enrich_properties_with_rent(db)
        score_all_properties(db)
        logger.info("Pipeline complete")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        run_pipeline,
        trigger=IntervalTrigger(hours=6),
        id="scrape_and_score",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started — pipeline runs every 6 hours")


def stop_scheduler():
    scheduler.shutdown(wait=False)

"""
Orchestrates scoring for a single property and persists the Score row.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Property, Score
from app.scoring import wholesale, flip, rental, airbnb
import logging

logger = logging.getLogger(__name__)

STRATEGY_LABELS = {
    "wholesale": "Wholesale",
    "flip": "Fix & Flip",
    "rental": "Long-Term Rental",
    "airbnb": "Airbnb / STR",
}


def score_property(prop: Property) -> dict:
    asking = prop.asking_price or 0
    zestimate = prop.zestimate or asking
    sqft = prop.sqft or 1200
    rent = prop.estimated_rent

    w = wholesale.score(asking, zestimate, sqft)
    f = flip.score(asking, zestimate, sqft)
    r = rental.score(asking, rent, sqft)
    a = airbnb.score(asking, rent, sqft)

    scores = {
        "wholesale": w["score"],
        "flip": f["score"],
        "rental": r["score"],
        "airbnb": a["score"],
    }
    best_strategy = max(scores, key=scores.get)
    best_score = scores[best_strategy]

    return {
        "wholesale_score": w["score"],
        "wholesale_equity_pct": w["equity_pct"],
        "wholesale_max_offer": w["max_offer"],
        "wholesale_est_repairs": w["est_repairs"],

        "flip_score": f["score"],
        "flip_profit": f["profit"],
        "flip_margin_pct": f["margin_pct"],
        "flip_max_offer": f["max_offer"],

        "rental_score": r["score"],
        "rental_cap_rate": r["cap_rate"],
        "rental_monthly_rent": r["monthly_rent"],
        "rental_annual_cashflow": r["annual_cashflow"],

        "airbnb_score": a["score"],
        "airbnb_nightly_rate": a["nightly_rate"],
        "airbnb_monthly_revenue": a["monthly_revenue"],
        "airbnb_annual_yield": a["annual_yield"],

        "best_strategy": best_strategy,
        "best_score": best_score,
    }


def score_all_properties(db: Session) -> int:
    props = db.query(Property).all()
    updated = 0
    skipped = 0
    for prop in props:
        # FB Marketplace rentals have no stated sale price — they're acquisition
        # targets (message the landlord). Scoring would divide by zero / produce
        # bogus numbers, so we leave them unscored and render them specially in UI.
        if prop.asking_price is None:
            skipped += 1
            continue
        try:
            data = score_property(prop)
            score_row = db.query(Score).filter(Score.property_id == prop.id).first()
            if score_row:
                for k, v in data.items():
                    setattr(score_row, k, v)
                score_row.scored_at = datetime.utcnow()
            else:
                score_row = Score(property_id=prop.id, **data)
                db.add(score_row)
            updated += 1
        except Exception as e:
            logger.error(f"Scoring error for property {prop.id}: {e}")
    db.commit()
    logger.info(f"Scoring complete — {updated} properties scored, {skipped} skipped (no asking price)")
    return updated

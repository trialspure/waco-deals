from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import AppSettings
from app.config import settings as app_config

router = APIRouter(prefix="/settings", tags=["settings"])

SETTING_KEYS = [
    "repair_cost_per_sqft",
    "wholesale_good_equity_pct", "wholesale_ok_equity_pct",
    "flip_good_margin_pct", "flip_ok_margin_pct", "flip_min_profit_dollars",
    "rental_good_cap_rate", "rental_ok_cap_rate", "rental_expense_ratio",
    "airbnb_occupancy_rate", "airbnb_nightly_rate_multiplier",
    "airbnb_good_yield", "airbnb_ok_yield",
    "rent_per_sqft_fallback",
]


@router.get("/")
def get_settings(db: Session = Depends(get_db)):
    overrides = {s.key: s.value for s in db.query(AppSettings).all()}
    result = {}
    for key in SETTING_KEYS:
        default = getattr(app_config, key, None)
        result[key] = float(overrides.get(key, default)) if default is not None else None
    return result


@router.put("/")
def update_settings(payload: dict, db: Session = Depends(get_db)):
    for key, value in payload.items():
        if key not in SETTING_KEYS:
            continue
        row = db.query(AppSettings).filter(AppSettings.key == key).first()
        if row:
            row.value = str(value)
        else:
            db.add(AppSettings(key=key, value=str(value)))
        # Also update live config
        if hasattr(app_config, key):
            setattr(app_config, key, float(value))
    db.commit()
    return {"status": "ok"}

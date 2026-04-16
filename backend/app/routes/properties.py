from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from app.database import get_db
from app.models import Property, Score

router = APIRouter(prefix="/properties", tags=["properties"])


class ScoreOut(BaseModel):
    wholesale_score: Optional[float]
    wholesale_equity_pct: Optional[float]
    wholesale_max_offer: Optional[float]
    wholesale_est_repairs: Optional[float]
    flip_score: Optional[float]
    flip_profit: Optional[float]
    flip_margin_pct: Optional[float]
    flip_max_offer: Optional[float]
    rental_score: Optional[float]
    rental_cap_rate: Optional[float]
    rental_monthly_rent: Optional[float]
    rental_annual_cashflow: Optional[float]
    airbnb_score: Optional[float]
    airbnb_nightly_rate: Optional[float]
    airbnb_monthly_revenue: Optional[float]
    airbnb_annual_yield: Optional[float]
    best_strategy: Optional[str]
    best_score: Optional[float]

    class Config:
        from_attributes = True


class PropertyOut(BaseModel):
    id: int
    zpid: Optional[str]
    address: str
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    beds: Optional[float]
    baths: Optional[float]
    sqft: Optional[float]
    year_built: Optional[int]
    property_type: Optional[str]
    asking_price: Optional[float]
    zestimate: Optional[float]
    price_per_sqft: Optional[float]
    days_on_market: Optional[int]
    estimated_rent: Optional[float]
    agent_name: Optional[str]
    agent_email: Optional[str]
    agent_phone: Optional[str]
    brokerage: Optional[str]
    is_saved: bool = False
    listing_url: Optional[str]
    photo_url: Optional[str]
    description: Optional[str]
    scores: Optional[ScoreOut]

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PropertyOut])
def list_properties(
    db: Session = Depends(get_db),
    strategy: Optional[str] = Query(None, description="Filter by best_strategy: wholesale|flip|rental|airbnb"),
    min_score: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    min_price: Optional[float] = Query(None),
    zip_code: Optional[str] = Query(None),
    min_beds: Optional[float] = Query(None),
    sort_by: str = Query("best_score", description="best_score|asking_price|days_on_market"),
    saved_only: bool = Query(False),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
):
    query = db.query(Property).join(Score, Property.id == Score.property_id, isouter=True)

    if saved_only:
        query = query.filter(Property.is_saved == True)  # noqa: E712
    if strategy:
        query = query.filter(Score.best_strategy == strategy)
    if min_score is not None:
        query = query.filter(Score.best_score >= min_score)
    if max_price is not None:
        query = query.filter(Property.asking_price <= max_price)
    if min_price is not None:
        query = query.filter(Property.asking_price >= min_price)
    if zip_code:
        query = query.filter(Property.zip_code == zip_code)
    if min_beds is not None:
        query = query.filter(Property.beds >= min_beds)

    if sort_by == "asking_price":
        query = query.order_by(Property.asking_price.asc())
    elif sort_by == "days_on_market":
        query = query.order_by(Property.days_on_market.asc())
    else:
        query = query.order_by(Score.best_score.desc().nullslast())

    return query.offset(offset).limit(limit).all()


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(property_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.post("/{property_id}/toggle-save", response_model=PropertyOut)
def toggle_save(property_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    prop.is_saved = not prop.is_saved
    db.commit()
    db.refresh(prop)
    return prop

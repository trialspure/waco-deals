"""
AI-powered investment analysis for a property using Claude.
POST /properties/{property_id}/analysis
Returns pros/cons + recommendation for each of the 4 strategies.
"""
import anthropic
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Property
from app.config import settings

router = APIRouter(prefix="/properties", tags=["analysis"])
logger = logging.getLogger(__name__)


class AnalysisResponse(BaseModel):
    property_id: int
    address: str
    analysis: str


def _fmt(val, prefix="$", suffix="", decimals=0) -> str:
    if val is None:
        return "N/A"
    if prefix == "$":
        return f"${val:,.{decimals}f}"
    if suffix == "%":
        return f"{val:.{decimals}f}%"
    return str(val)


@router.post("/{property_id}/analysis", response_model=AnalysisResponse)
def generate_analysis(property_id: int, db: Session = Depends(get_db)):
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY not configured. Add it to your .env file.",
        )

    prop = db.query(Property).filter(Property.id == property_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    s = prop.scores

    property_block = f"""
PROPERTY: {prop.address}, {prop.city}, {prop.state} {prop.zip_code}
Asking Price:    {_fmt(prop.asking_price)}
Zestimate (ARV): {_fmt(prop.zestimate)}
Beds / Baths:    {prop.beds or "?"} bed / {prop.baths or "?"} bath
Sqft:            {_fmt(prop.sqft, prefix="", suffix=" sqft")}
Year Built:      {prop.year_built or "unknown"}
Days on Market:  {prop.days_on_market or "unknown"}
Property Type:   {(prop.property_type or "").replace("_", " ")}
""".strip()

    scores_block = ""
    if s:
        scores_block = f"""
INVESTMENT SCORES (1–10 scale):
  Wholesale:       {_fmt(s.wholesale_score, prefix="", decimals=1)}/10
    Equity %:      {_fmt(s.wholesale_equity_pct, prefix="", suffix="%", decimals=1)}
    Max Offer:     {_fmt(s.wholesale_max_offer)}
    Est. Repairs:  {_fmt(s.wholesale_est_repairs)}

  Fix & Flip:      {_fmt(s.flip_score, prefix="", decimals=1)}/10
    Est. Profit:   {_fmt(s.flip_profit)}
    Margin:        {_fmt(s.flip_margin_pct, prefix="", suffix="%", decimals=1)}
    Max Offer:     {_fmt(s.flip_max_offer)}

  Long-Term Rental: {_fmt(s.rental_score, prefix="", decimals=1)}/10
    Monthly Rent:  {_fmt(s.rental_monthly_rent)}
    Cap Rate:      {_fmt(s.rental_cap_rate, prefix="", suffix="%", decimals=1)}
    Annual Cash Flow: {_fmt(s.rental_annual_cashflow)}

  Airbnb / STR:    {_fmt(s.airbnb_score, prefix="", decimals=1)}/10
    Est. Nightly:  {_fmt(s.airbnb_nightly_rate)}
    Monthly Rev:   {_fmt(s.airbnb_monthly_revenue)}
    Gross Yield:   {_fmt(s.airbnb_annual_yield, prefix="", suffix="%", decimals=1)}

  Best Strategy: {s.best_strategy or "N/A"} (score: {_fmt(s.best_score, prefix="", decimals=1)}/10)
""".strip()

    prompt = f"""You are a real estate investment analyst helping evaluate a property in Waco, TX for a real estate investor.

Here is the property data:

{property_block}

{scores_block}

Write a professional investment analysis that covers all four strategies: Wholesale, Fix & Flip, Long-Term Rental, and Airbnb/STR.

For EACH strategy, provide:
- 2–3 bullet point PROS (specific reasons this property works for this strategy)
- 2–3 bullet point CONS (specific reasons it may not work)
- One sentence bottom-line recommendation

After all four strategies, add a short "Overall Recommendation" paragraph (3–5 sentences) naming the best strategy and why, and any key risks to watch out for.

Format it cleanly with clear headers for each strategy. Keep the tone professional but easy to read — this will be shared with a supervisor. Be specific to the actual numbers, not generic advice."""

    try:
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
        )
        analysis_text = message.content[0].text
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=503, detail="Invalid Anthropic API key.")
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        raise HTTPException(status_code=502, detail="Failed to generate analysis.")

    return AnalysisResponse(
        property_id=property_id,
        address=prop.address,
        analysis=analysis_text,
    )

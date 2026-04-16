from app.config import settings


def score(asking_price: float, monthly_rent: float, sqft: float = None) -> dict:
    """
    Airbnb / STR scoring.
    Estimates nightly rate as a premium over long-term rent, then applies occupancy.
    Gross yield = Annual STR Revenue / Asking Price
    """
    if not asking_price or asking_price <= 0:
        return {"score": 1, "nightly_rate": 0, "monthly_revenue": 0, "annual_yield": 0}

    if not monthly_rent or monthly_rent <= 0:
        sqft = sqft or 1200
        monthly_rent = sqft * settings.rent_per_sqft_fallback

    # Nightly rate = (LTR monthly rent × STR multiplier) / 30
    nightly_rate = (monthly_rent * settings.airbnb_nightly_rate_multiplier) / 30
    monthly_revenue = nightly_rate * 30 * settings.airbnb_occupancy_rate
    annual_revenue = monthly_revenue * 12
    annual_yield = (annual_revenue / asking_price) * 100

    good = settings.airbnb_good_yield
    ok = settings.airbnb_ok_yield

    if annual_yield >= good:
        score_val = round(8 + min(2, (annual_yield - good) / 4), 1)
    elif annual_yield >= ok:
        score_val = round(5 + (annual_yield - ok) / (good - ok) * 3, 1)
    else:
        score_val = max(1.0, round(1 + max(0, annual_yield) / ok * 4, 1))

    return {
        "score": min(10.0, score_val),
        "nightly_rate": round(nightly_rate, 2),
        "monthly_revenue": round(monthly_revenue, 2),
        "annual_yield": round(annual_yield, 2),
    }

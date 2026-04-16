from app.config import settings


def score(asking_price: float, monthly_rent: float, sqft: float = None) -> dict:
    """
    Long-term rental scoring.
    Cap rate = NOI / Price  (NOI = Annual Rent × (1 − expense_ratio))
    """
    if not asking_price or asking_price <= 0:
        return {"score": 1, "cap_rate": 0, "monthly_rent": 0, "annual_cashflow": 0}

    if not monthly_rent or monthly_rent <= 0:
        sqft = sqft or 1200
        monthly_rent = sqft * settings.rent_per_sqft_fallback

    annual_rent = monthly_rent * 12
    noi = annual_rent * (1 - settings.rental_expense_ratio)
    cap_rate = (noi / asking_price) * 100
    annual_cashflow = noi  # assumes cash purchase; for financed, subtract debt service

    rent_to_price = (monthly_rent / asking_price) * 100  # 1% rule check

    good = settings.rental_good_cap_rate
    ok = settings.rental_ok_cap_rate

    if cap_rate >= good:
        score_val = round(8 + min(2, (cap_rate - good) / 2), 1)
    elif cap_rate >= ok:
        score_val = round(5 + (cap_rate - ok) / (good - ok) * 3, 1)
    else:
        score_val = max(1.0, round(1 + max(0, cap_rate) / ok * 4, 1))

    return {
        "score": min(10.0, score_val),
        "cap_rate": round(cap_rate, 2),
        "monthly_rent": round(monthly_rent, 2),
        "annual_cashflow": round(annual_cashflow, 2),
        "rent_to_price_pct": round(rent_to_price, 3),
    }

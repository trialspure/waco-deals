from app.config import settings


def score(asking_price: float, zestimate: float, sqft: float, repair_cost_per_sqft: float = None) -> dict:
    """
    Wholesale scoring using the 70% rule.
    Max offer = ARV × 0.70 − Estimated Repairs
    """
    if not asking_price or not zestimate or zestimate <= 0:
        return {"score": 1, "equity_pct": 0, "max_offer": 0, "est_repairs": 0}

    rps = repair_cost_per_sqft or settings.repair_cost_per_sqft
    est_repairs = (sqft or 1200) * rps
    max_offer = zestimate * 0.70 - est_repairs
    equity_pct = ((zestimate - asking_price) / zestimate) * 100

    # Score 1-10
    good = settings.wholesale_good_equity_pct
    ok = settings.wholesale_ok_equity_pct
    if equity_pct >= good and asking_price <= max_offer:
        score_val = round(8 + min(2, (equity_pct - good) / 10), 1)
    elif equity_pct >= ok:
        score_val = round(5 + (equity_pct - ok) / (good - ok) * 3, 1)
    else:
        score_val = max(1.0, round(1 + max(0, equity_pct) / ok * 4, 1))

    return {
        "score": min(10.0, score_val),
        "equity_pct": round(equity_pct, 2),
        "max_offer": round(max_offer, 2),
        "est_repairs": round(est_repairs, 2),
    }

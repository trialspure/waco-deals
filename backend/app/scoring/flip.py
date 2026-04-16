from app.config import settings

SELLING_COST_RATIO = 0.09  # ~9% of ARV (agent fees, closing costs, etc.)
HOLDING_COST_RATIO = 0.03  # ~3% of ARV for 6-month hold


def score(asking_price: float, zestimate: float, sqft: float, repair_cost_per_sqft: float = None) -> dict:
    """
    Fix & Flip scoring.
    Profit = ARV − asking − repairs − selling costs − holding costs
    """
    if not asking_price or not zestimate or zestimate <= 0:
        return {"score": 1, "profit": 0, "margin_pct": 0, "max_offer": 0}

    rps = repair_cost_per_sqft or settings.repair_cost_per_sqft
    est_repairs = (sqft or 1200) * rps
    selling_costs = zestimate * SELLING_COST_RATIO
    holding_costs = zestimate * HOLDING_COST_RATIO

    profit = zestimate - asking_price - est_repairs - selling_costs - holding_costs
    margin_pct = (profit / zestimate) * 100 if zestimate else 0

    # Max offer: work backwards — what asking price yields 20% margin?
    max_offer = zestimate * (1 - SELLING_COST_RATIO - HOLDING_COST_RATIO) - est_repairs - (zestimate * 0.20)

    good_margin = settings.flip_good_margin_pct
    ok_margin = settings.flip_ok_margin_pct
    min_profit = settings.flip_min_profit_dollars

    if margin_pct >= good_margin and profit >= min_profit:
        score_val = round(8 + min(2, (margin_pct - good_margin) / 5), 1)
    elif margin_pct >= ok_margin:
        score_val = round(5 + (margin_pct - ok_margin) / (good_margin - ok_margin) * 3, 1)
    else:
        score_val = max(1.0, round(1 + max(0, margin_pct) / ok_margin * 4, 1))

    return {
        "score": min(10.0, score_val),
        "profit": round(profit, 2),
        "margin_pct": round(margin_pct, 2),
        "max_offer": round(max_offer, 2),
    }

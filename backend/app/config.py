from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env relative to this file's location (backend/)
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8")

    database_url: str = "postgresql://waco:waco_secret@localhost:5432/waco_deals"
    hasdata_api_key: str = ""
    rapidapi_key: str = ""
    rentcast_api_key: str = ""
    repair_cost_per_sqft: float = 25.0

    # Scoring thresholds (all user-adjustable via settings page)
    wholesale_good_equity_pct: float = 30.0
    wholesale_ok_equity_pct: float = 15.0

    flip_good_margin_pct: float = 20.0
    flip_ok_margin_pct: float = 10.0
    flip_min_profit_dollars: float = 20000.0

    rental_good_cap_rate: float = 8.0
    rental_ok_cap_rate: float = 5.0
    rental_expense_ratio: float = 0.5

    airbnb_occupancy_rate: float = 0.55
    airbnb_nightly_rate_multiplier: float = 1.4
    airbnb_good_yield: float = 12.0
    airbnb_ok_yield: float = 8.0

    rent_per_sqft_fallback: float = 1.10


settings = Settings()

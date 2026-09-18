import os
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database
DEFAULT_DB_PATH = DATA_DIR / "price_monitor.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Scraper configuration
DEFAULT_USER_AGENT = os.getenv(
    "USER_AGENT",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))

# Alerting defaults
DEFAULT_PRICE_CHANGE_THRESHOLD_PCT = float(os.getenv("PRICE_CHANGE_THRESHOLD_PCT", "5.0"))
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
ALERT_EMAIL_RECIPIENT = os.getenv("ALERT_EMAIL_RECIPIENT", "")

# Currency conversion rates relative to USD
EXCHANGE_RATES = {
    "USD": {"rate": 1.0, "symbol": "$"},
    "EUR": {"rate": 0.92, "symbol": "€"},
    "GBP": {"rate": 0.79, "symbol": "£"},
    "INR": {"rate": 83.50, "symbol": "₹"},
    "JPY": {"rate": 155.00, "symbol": "¥"},
    "CAD": {"rate": 1.36, "symbol": "C$"},
}


def convert_and_format_price(amount_usd: Optional[float], currency_code: str = "USD") -> str:
    if amount_usd is None:
        return "N/A"
    curr_info = EXCHANGE_RATES.get(currency_code.upper(), EXCHANGE_RATES["USD"])
    converted = amount_usd * curr_info["rate"]
    symbol = curr_info["symbol"]
    if currency_code.upper() in ("JPY", "KRW"):
        return f"{symbol}{converted:,.0f}"
    return f"{symbol}{converted:,.2f}"
"""Currency Service: Fetches real-time cryptocurrency & fiat rates for FET & USD."""

import logging
from typing import Dict
import requests

logger = logging.getLogger("AeroVoyage.Currency")

FALLBACK_FET_PRICE_USD = 1.35


def get_fet_price_usd() -> float:
    """Fetch live FET price in USD with instant fallback."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=fetch-ai&vs_currencies=usd"
        res = requests.get(url, timeout=2.0)
        if res.status_code == 200:
            data = res.json()
            price = data.get("fetch-ai", {}).get("usd")
            if price and price > 0:
                return float(price)
    except Exception as exc:
        logger.debug(f"Live FET price query fallback triggered ({exc})")

    return FALLBACK_FET_PRICE_USD


def convert_usd_to_fet(amount_usd: float) -> float:
    rate = get_fet_price_usd()
    return round(amount_usd / rate, 2)


def convert_fet_to_usd(amount_fet: float) -> float:
    rate = get_fet_price_usd()
    return round(amount_fet * rate, 2)

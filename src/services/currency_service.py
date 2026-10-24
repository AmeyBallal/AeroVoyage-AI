"""Currency Service: Fetches real-time cryptocurrency & fiat rates for FET & USD."""

import logging
import time
from typing import Dict, Optional
import requests

logger = logging.getLogger("AeroVoyage.Currency")

FALLBACK_FET_PRICE_USD = 1.35
_CACHED_RATE: Optional[float] = None
_CACHE_TIMESTAMP: float = 0.0
_CACHE_TTL: float = 60.0  # 60 seconds cache


def get_fet_price_usd() -> float:
    """Fetch live FET price in USD with instant fallback and short TTL cache."""
    global _CACHED_RATE, _CACHE_TIMESTAMP
    now = time.time()
    if _CACHED_RATE is not None and (now - _CACHE_TIMESTAMP) < _CACHE_TTL:
        return _CACHED_RATE

    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=fetch-ai&vs_currencies=usd"
        res = requests.get(url, timeout=2.0)
        if res.status_code == 200:
            data = res.json()
            price = data.get("fetch-ai", {}).get("usd")
            if price and float(price) > 0:
                _CACHED_RATE = float(price)
                _CACHE_TIMESTAMP = now
                return _CACHED_RATE
    except Exception as exc:
        logger.debug(f"Live FET price query fallback triggered ({exc})")

    if _CACHED_RATE is not None:
        return _CACHED_RATE
    return FALLBACK_FET_PRICE_USD


def convert_usd_to_fet(amount_usd: float) -> float:
    rate = get_fet_price_usd()
    return round(amount_usd / rate, 2)


def convert_fet_to_usd(amount_fet: float) -> float:
    rate = get_fet_price_usd()
    return round(amount_fet * rate, 2)

"""Public market-price reference feed for the simulation-only demo.

Uses Binance's documented public market-data endpoint without credentials.
SAR values are indicative conversions using 3.75 SAR per USDT, not direct SAR order-book quotes.
"""
from datetime import datetime, timezone
import json
import time
from threading import Lock
from urllib.error import URLError
from urllib.request import Request, urlopen

SAR_PER_USDT_REFERENCE = 3.75
ASSET_SYMBOLS = {
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "BNB": "BNBUSDT",
    "SOL": "SOLUSDT",
    "XRP": "XRPUSDT",
    "ADA": "ADAUSDT",
    "DOGE": "DOGEUSDT",
    "TRX": "TRXUSDT",
    "LTC": "LTCUSDT",
    "DOT": "DOTUSDT",
    "LINK": "LINKUSDT",
    "USDC": "USDCUSDT",
}
_CACHE_SECONDS = 15
_cache_lock = Lock()
_cache_at = 0.0
_cache = None


def get_live_prices_sar():
    """Return a symbol-to-price record map, or None when public data is unavailable."""
    global _cache_at, _cache
    now = time.monotonic()
    with _cache_lock:
        if _cache is not None and now - _cache_at < _CACHE_SECONDS:
            return _cache
        if _cache is None and _cache_at and now - _cache_at < 10:
            return None

        symbols = list(ASSET_SYMBOLS.values())
        encoded = __import__("urllib.parse", fromlist=["quote"]).quote(
            json.dumps(symbols, separators=(",", ":")), safe=""
        )
        url = "https://data-api.binance.vision/api/v3/ticker/price?symbols=" + encoded
        request = Request(url, headers={"User-Agent": "SI-Exchange-Simulation/0.1"})
        try:
            with urlopen(request, timeout=4) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, list):
                raise ValueError("Unexpected market-data response")
            raw = {item["symbol"]: float(item["price"]) for item in payload}
            timestamp = datetime.now(timezone.utc).isoformat()
            result = {}
            for asset, pair in ASSET_SYMBOLS.items():
                value = raw.get(pair)
                if value is None or value <= 0:
                    continue
                result[f"{asset}/SAR"] = {
                    "price_sar": round(value * SAR_PER_USDT_REFERENCE, 8),
                    "is_live": True,
                    "price_source": "Binance Spot public ticker; SAR conversion is indicative at 3.75 SAR/USDT",
                    "updated_at": timestamp,
                }
            result["USDT/SAR"] = {
                "price_sar": SAR_PER_USDT_REFERENCE,
                "is_live": False,
                "price_source": "Reference peg only (3.75 SAR/USDT); not a live SAR market quote",
                "updated_at": timestamp,
            }
            result["USDC/SAR"]["price_source"] += " (USDC/USDT market pair)"
            _cache = result
            _cache_at = time.monotonic()
            return result
        except (OSError, URLError, TimeoutError, ValueError, KeyError, TypeError, json.JSONDecodeError):
            _cache = None
            _cache_at = time.monotonic()
            return None

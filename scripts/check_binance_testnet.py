"""Read-only connectivity smoke test for a dedicated Binance Spot Testnet account."""
from __future__ import annotations

import json
import sys

from app.binance_testnet import BinanceSpotTestnetAdapter


def main() -> int:
    try:
        adapter = BinanceSpotTestnetAdapter()
        result = adapter.check_connection()
    except Exception as exc:
        # Never print credentials or request headers; show only exception class and sanitized message.
        message = str(exc).replace("\n", " ")[:240]
        print(json.dumps({
            "connected": False,
            "mode": "external_testnet_only",
            "error_type": type(exc).__name__,
            "error": message,
        }))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

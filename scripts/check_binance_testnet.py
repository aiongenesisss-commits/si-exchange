"""Read-only connectivity smoke test for a dedicated Binance Spot Testnet account."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Support direct execution as python scripts/check_binance_testnet.py by
# making the repository root importable (Python otherwise starts at scripts/).
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.binance_testnet import BinanceSpotTestnetAdapter


def main() -> int:
    try:
        adapter = BinanceSpotTestnetAdapter()
        result = adapter.check_connection()
    except Exception as exc:
        # Never print credentials or request headers; show only exception class and sanitized message.
        message = str(exc).replace("\\n", " ")[:240]
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

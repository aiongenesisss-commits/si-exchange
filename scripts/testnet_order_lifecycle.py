"""Optional Binance Spot TESTNET order lifecycle smoke test.

No order is submitted unless ALLOW_TESTNET_ORDER=true is explicitly set.
Uses testnet funds only. If querying fails after submission, attempts best-effort cancellation.
"""
from __future__ import annotations

import json
import os
import sys
import time

from app.binance_testnet import BinanceSpotTestnetAdapter


def main() -> int:
    if os.getenv("ALLOW_TESTNET_ORDER", "false").strip().lower() not in {"true", "1", "yes"}:
        print(json.dumps({
            "mode": "external_testnet_only",
            "submitted": False,
            "reason": "Order lifecycle disabled. Set ALLOW_TESTNET_ORDER=true in the manual test workflow to opt in.",
        }))
        return 0

    adapter = BinanceSpotTestnetAdapter()
    client_id = "aion-smoke-" + str(int(time.time()))
    order_id = None
    try:
        order = adapter.submit_order(
            market="BTC/USDT",
            side="buy",
            price="1000",
            quantity="0.01",
            idempotency_key=client_id,
        )
        order_id = order.order_id
        queried = adapter.get_order(order_id)
        result = {
            "mode": "external_testnet_only",
            "submitted": True,
            "order_id": order.order_id,
            "queried_status": queried.status,
            "market": order.market,
            "limit_price": order.price,
            "quantity": order.quantity,
        }
        if queried.status == "open":
            cancelled = adapter.cancel_order(order_id)
            result["cancel_status"] = cancelled.status
        else:
            result["cancel_status"] = "not_cancelled_order_not_open"
        print(json.dumps(result, sort_keys=True))
        return 0
    except Exception as exc:
        # If a submit succeeded but a later request failed, make a best-effort cleanup attempt.
        # A cancellation failure is reported by type only; never print request data or credentials.
        cleanup_status = "not_needed"
        if order_id is not None:
            try:
                cancelled = adapter.cancel_order(order_id)
                cleanup_status = cancelled.status
            except Exception as cleanup_exc:
                cleanup_status = "failed:" + type(cleanup_exc).__name__
        print(json.dumps({
            "mode": "external_testnet_only",
            "submitted": order_id is not None,
            "order_id": order_id,
            "cleanup_status": cleanup_status,
            "error_type": type(exc).__name__,
            "error": str(exc).replace("\\n", " ")[:240],
            "warning": "A timeout may leave the exchange outcome unknown. Inspect the testnet account before retrying.",
        }))
        return 1


if __name__ == "__main__":
    sys.exit(main())

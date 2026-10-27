"""Binance Spot TESTNET adapter. The endpoint is deliberately hard-coded to testnet."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from threading import Lock
from typing import Literal

from app.execution import ExecutionOrder

TESTNET_BASE_URL = "https://testnet.binance.vision"
SYMBOL_RE = re.compile(r"^[A-Z0-9]{5,20}$")


class BinanceSpotTestnetAdapter:
    """Uses Binance Spot Testnet only; never accepts a configurable base URL."""

    mode = "external_testnet_only"

    def __init__(self, api_key: str | None = None, api_secret: str | None = None, timeout: float = 8.0):
        self.api_key = api_key if api_key is not None else os.getenv("BINANCE_TESTNET_API_KEY", "")
        self.api_secret = api_secret if api_secret is not None else os.getenv("BINANCE_TESTNET_API_SECRET", "")
        if not self.api_key or not self.api_secret:
            raise RuntimeError("Binance Spot Testnet credentials are required; configure server-side testnet secrets")
        if timeout <= 0 or timeout > 30:
            raise ValueError("timeout must be greater than 0 and at most 30 seconds")
        self.timeout = timeout
        self._lock = Lock()
        self._orders: dict[str, tuple[str, ExecutionOrder]] = {}

    @staticmethod
    def _symbol(market: str) -> str:
        # Deliberately disallow SAR pairs: Binance Spot Testnet symbols must be real exchange symbols.
        normalized = market.replace("/", "").upper()
        if not SYMBOL_RE.fullmatch(normalized) or not normalized.endswith("USDT"):
            raise ValueError("Only explicit Binance Spot Testnet USDT pairs such as BTC/USDT are supported")
        return normalized

    def _request(self, method: str, path: str, params: dict[str, str] | None = None, *, signed: bool = True):
        values = dict(params or {})
        headers = {"X-MBX-APIKEY": self.api_key}
        if signed:
            values["timestamp"] = str(int(time.time() * 1000))
            values["recvWindow"] = "5000"
            query = urllib.parse.urlencode(values)
            values["signature"] = hmac.new(
                self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
            ).hexdigest()
        encoded = urllib.parse.urlencode(values)
        url = TESTNET_BASE_URL + path
        data = None
        if method in {"GET", "DELETE"}:
            if encoded:
                url += "?" + encoded
        else:
            data = encoded.encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = response.read()
            result = json.loads(payload.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read(2048).decode("utf-8", errors="replace")
            raise RuntimeError(f"Binance Spot Testnet HTTP {exc.code}: {body}") from None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Binance Spot Testnet request failed: {type(exc).__name__}") from None
        if isinstance(result, dict) and "code" in result and result.get("code", 0) < 0:
            raise RuntimeError(f"Binance Spot Testnet API error {result.get('code')}: {result.get('msg', 'unknown error')}")
        return result

    @staticmethod
    def _to_order(data: dict, market: str) -> ExecutionOrder:
        raw_status = str(data.get("status", "NEW")).upper()
        status = "cancelled" if raw_status in {"CANCELED", "CANCELLED", "EXPIRED", "REJECTED"} else (
            "filled" if raw_status == "FILLED" else "open"
        )
        created_ms = data.get("transactTime") or data.get("time") or int(time.time() * 1000)
        created_at = datetime.fromtimestamp(int(created_ms) / 1000, tz=timezone.utc).isoformat()
        return ExecutionOrder(
            order_id=str(data.get("orderId", data.get("clientOrderId", ""))),
            market=market,
            side=str(data.get("side", "BUY")).lower(),
            price=str(data.get("price", "0")),
            quantity=str(data.get("origQty", "0")),
            status=status,
            created_at=created_at,
        )

    def submit_order(
        self, *, market: str, side: Literal["buy", "sell"], price: str,
        quantity: str, idempotency_key: str
    ) -> ExecutionOrder:
        from decimal import Decimal, InvalidOperation
        if side not in {"buy", "sell"}:
            raise ValueError("side must be buy or sell")
        if not idempotency_key or len(idempotency_key) > 32 or not re.fullmatch(r"[A-Za-z0-9_-]+", idempotency_key):
            raise ValueError("idempotency_key must be 1-32 letters, digits, underscore, or hyphen")
        try:
            p, q = Decimal(price), Decimal(quantity)
        except (InvalidOperation, TypeError, ValueError):
            raise ValueError("price and quantity must be decimal strings") from None
        if not p.is_finite() or not q.is_finite() or p <= 0 or q <= 0:
            raise ValueError("price and quantity must be finite positive decimals")
        symbol = self._symbol(market)
        # Binance's client order ID is the exchange-side idempotency handle.
        response = self._request("POST", "/api/v3/order", {
            "symbol": symbol, "side": side.upper(), "type": "LIMIT",
            "timeInForce": "GTC", "quantity": format(q, "f"),
            "price": format(p, "f"), "newClientOrderId": idempotency_key,
            "newOrderRespType": "FULL",
        })
        order = self._to_order(response, market.upper())
        with self._lock:
            self._orders[order.order_id] = (symbol, order)
        return order

    def get_order(self, order_id: str) -> ExecutionOrder:
        with self._lock:
            saved = self._orders.get(str(order_id))
        if saved is None:
            raise KeyError("unknown testnet order in this process; order registry is not durable")
        symbol, original = saved
        response = self._request("GET", "/api/v3/order", {"symbol": symbol, "orderId": str(order_id)})
        order = self._to_order(response, original.market)
        with self._lock:
            self._orders[order.order_id] = (symbol, order)
        return order

    def cancel_order(self, order_id: str) -> ExecutionOrder:
        with self._lock:
            saved = self._orders.get(str(order_id))
        if saved is None:
            raise KeyError("unknown testnet order in this process; order registry is not durable")
        symbol, original = saved
        response = self._request("DELETE", "/api/v3/order", {"symbol": symbol, "orderId": str(order_id)})
        order = self._to_order(response, original.market)
        with self._lock:
            self._orders[order.order_id] = (symbol, order)
        return order

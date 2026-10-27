"""Provider-neutral order execution interface with an in-process demo adapter only.

This module does not connect to an exchange, broker, wallet, or external sandbox.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import Lock
from typing import Literal, Protocol
from uuid import uuid4


OrderStatus = Literal["open", "cancelled"]


@dataclass(frozen=True)
class ExecutionOrder:
    order_id: str
    market: str
    side: Literal["buy", "sell"]
    price: str
    quantity: str
    status: OrderStatus
    created_at: str


class ExecutionAdapter(Protocol):
    """Small provider-neutral contract; implementations must document their trust boundary."""

    def submit_order(
        self, *, market: str, side: Literal["buy", "sell"], price: str,
        quantity: str, idempotency_key: str
    ) -> ExecutionOrder: ...

    def get_order(self, order_id: str) -> ExecutionOrder: ...

    def cancel_order(self, order_id: str) -> ExecutionOrder: ...


class InProcessSandboxAdapter:
    """Deterministic local demo adapter. It never sends orders to a real provider."""

    mode = "simulation_only"

    def __init__(self) -> None:
        self._lock = Lock()
        self._orders: dict[str, ExecutionOrder] = {}
        self._idempotency: dict[str, tuple[tuple[str, str, str, str], str]] = {}

    def submit_order(
        self, *, market: str, side: Literal["buy", "sell"], price: str,
        quantity: str, idempotency_key: str
    ) -> ExecutionOrder:
        if not market.strip():
            raise ValueError("market is required")
        if side not in ("buy", "sell"):
            raise ValueError("side must be buy or sell")
        if not idempotency_key or len(idempotency_key) > 200:
            raise ValueError("a non-empty idempotency key of at most 200 characters is required")
        # Decimal strings are retained as provided; no binary float conversion occurs here.
        try:
            from decimal import Decimal, InvalidOperation
            p, q = Decimal(price), Decimal(quantity)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError("price and quantity must be decimal strings") from exc
        if not p.is_finite() or not q.is_finite() or p <= 0 or q <= 0:
            raise ValueError("price and quantity must be finite positive decimals")
        fingerprint = (market, side, str(p), str(q))
        with self._lock:
            prior = self._idempotency.get(idempotency_key)
            if prior:
                if prior[0] != fingerprint:
                    raise ValueError("idempotency key reused with a different order")
                return self._orders[prior[1]]
            order_id = str(uuid4())
            order = ExecutionOrder(
                order_id=order_id, market=market, side=side, price=str(p),
                quantity=str(q), status="open",
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            self._orders[order_id] = order
            self._idempotency[idempotency_key] = (fingerprint, order_id)
            return order

    def get_order(self, order_id: str) -> ExecutionOrder:
        with self._lock:
            try:
                return self._orders[order_id]
            except KeyError:
                raise KeyError("unknown sandbox order") from None

    def cancel_order(self, order_id: str) -> ExecutionOrder:
        with self._lock:
            order = self._orders.get(order_id)
            if order is None:
                raise KeyError("unknown sandbox order")
            if order.status == "cancelled":
                return order
            cancelled = ExecutionOrder(
                order_id=order.order_id, market=order.market, side=order.side,
                price=order.price, quantity=order.quantity, status="cancelled",
                created_at=order.created_at,
            )
            self._orders[order_id] = cancelled
            return cancelled


def build_execution_adapter(mode: str | None = None) -> ExecutionAdapter:
    """Return only the local demo adapter; reject live/unknown configuration closed."""
    configured = (mode if mode is not None else os.getenv("EXECUTION_MODE", "simulation")).strip().lower()
    live_flag = os.getenv("REAL_TRADING_ENABLED", "false").strip().lower()
    if live_flag not in {"false", "0", "no", "true", "1", "yes"}:
        raise RuntimeError("REAL_TRADING_ENABLED must be an explicit boolean")
    if live_flag in {"true", "1", "yes"}:
        raise RuntimeError("Live trading is not implemented and cannot be enabled")
    if configured not in {"simulation", "sandbox"}:
        raise RuntimeError(f"Unsupported EXECUTION_MODE: {configured!r}; live execution is unavailable")
    return InProcessSandboxAdapter()

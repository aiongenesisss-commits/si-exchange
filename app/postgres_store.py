"""Transactional PostgreSQL persistence for the simulation-only SI Exchange demo.

Enabled only with AION_STORAGE_BACKEND=postgres and DATABASE_URL set.
Every order, balance update, fill, idempotency record and audit event is committed
in one transaction. This module never connects to a wallet or blockchain.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

ASSETS = {
    "BTC": Decimal("0.25"), "ETH": Decimal("2"), "BNB": Decimal("10"),
    "SOL": Decimal("20"), "XRP": Decimal("500"), "ADA": Decimal("500"),
    "DOGE": Decimal("1000"), "TRX": Decimal("5000"), "LTC": Decimal("2"),
    "DOT": Decimal("20"), "LINK": Decimal("20"), "AION": Decimal("100000"), "USDT": Decimal("1000"),
    "USDC": Decimal("1000"),
}
INITIAL_TOTALS = {"SAR": Decimal("200000"), **{k: v * 2 for k, v in ASSETS.items()}}


def _connect():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("AION_STORAGE_BACKEND=postgres requires DATABASE_URL; refusing volatile fallback")
    return psycopg.connect(url, row_factory=dict_row, connect_timeout=5)


def initialize_demo_accounts():
    """Idempotently seed demo-only accounts and initial balances, never reset existing balances."""
    with _connect() as conn:
        for account in ("A", "B"):
            conn.execute(
                "INSERT INTO demo_accounts(id,label,account_type) VALUES (%s,%s,'demo') ON CONFLICT(id) DO NOTHING",
                (account, f"Demo account {account}"),
            )
            for asset, amount in {"SAR": Decimal("100000"), **ASSETS}.items():
                conn.execute(
                    """INSERT INTO demo_balances(account_id,asset,available_amount)
                       VALUES (%s,%s,%s) ON CONFLICT(account_id,asset) DO NOTHING""",
                    (account, asset, amount),
                )
        conn.execute(
            """INSERT INTO demo_audit_events(event_type,entity_type,entity_id,details)
               VALUES ('storage_initialized','system','si-exchange',%s::jsonb)""",
            (json.dumps({"mode": "simulation_only", "seed": "insert-if-missing"}),),
        )


def check_connection():
    with _connect() as conn:
        conn.execute("SELECT 1").fetchone()


def _order(row):
    return {
        "id": str(row["id"]), "market": row["market"], "side": row["side"],
        "account": row["account_id"], "price": float(row["limit_price"]),
        "quantity": float(row["quantity"]), "remaining_quantity": float(row["remaining_quantity"]),
        "status": row["status"], "created_at": row["created_at"],
    }


def _fill(row):
    return {
        "id": str(row["id"]), "order_id": str(row["taker_order_id"]),
        "maker_order_id": str(row["maker_order_id"]), "taker_order_id": str(row["taker_order_id"]),
        "buyer_account": row["buyer_account_id"], "seller_account": row["seller_account_id"],
        "market": row["market"], "side": row["taker_side"], "price": float(row["execution_price"]),
        "quantity": float(row["quantity"]), "simulated_value_sar": float(row["simulated_value_sar"]),
        "created_at": row["created_at"],
    }


def balances():
    with _connect() as conn:
        rows = conn.execute("SELECT account_id,asset,available_amount FROM demo_balances ORDER BY account_id,asset").fetchall()
    result = {"A": {}, "B": {}}
    for row in rows:
        result[row["account_id"]][row["asset"]] = float(row["available_amount"])
    return {"mode": "demo_only", "balances": result}


def _reserved(conn, account, asset, exclude_order_ids=()):
    rows = conn.execute(
        """SELECT id,market,side,limit_price,remaining_quantity FROM demo_orders
           WHERE account_id=%s AND status IN ('open','partially_filled')""", (account,)
    ).fetchall()
    excluded = {str(value) for value in exclude_order_ids}
    total = Decimal(0)
    for row in rows:
        if str(row["id"]) in excluded:
            continue
        base = row["market"].split("/")[0]
        if asset == "SAR" and row["side"] == "buy":
            total += row["limit_price"] * row["remaining_quantity"]
        elif asset == base and row["side"] == "sell":
            total += row["remaining_quantity"]
    return total


def available_balances():
    with _connect() as conn:
        rows = conn.execute("SELECT account_id,asset,available_amount FROM demo_balances ORDER BY account_id,asset").fetchall()
        result = {"A": {}, "B": {}}
        for row in rows:
            reserved = _reserved(conn, row["account_id"], row["asset"])
            result[row["account_id"]][row["asset"]] = float(max(Decimal(0), row["available_amount"] - reserved))
    return {"mode": "demo_only", "available_balances": result}


def list_orders():
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM demo_orders ORDER BY created_at,id").fetchall()
    return [_order(row) for row in rows]


def get_order(order_id):
    with _connect() as conn:
        row = conn.execute("SELECT * FROM demo_orders WHERE id=%s", (order_id,)).fetchone()
    return _order(row) if row else None


def list_fills():
    with _connect() as conn:
        rows = conn.execute(
            """SELECT f.*,t.side AS taker_side FROM demo_fills f
               JOIN demo_orders t ON t.id=f.taker_order_id ORDER BY f.created_at,f.id"""
        ).fetchall()
    return [_fill(row) for row in rows]


def place_order(request, idempotency_key=None):
    """Create/match one order atomically under a database-wide transaction lock."""
    payload = request.model_dump(mode="json")
    fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    order_id = uuid4()
    now = datetime.now(timezone.utc)
    market, side, account = payload["market"], payload["side"], payload["account"]
    price, quantity = Decimal(str(payload["price"])), Decimal(str(payload["quantity"]))
    base = market.split("/")[0]

    with _connect() as conn:
        # Serializes matching across app workers so two concurrent requests cannot spend the same demo funds.
        conn.execute("SELECT pg_advisory_xact_lock(741002610)")
        if idempotency_key:
            prior = conn.execute(
                """SELECT k.request_fingerprint,o.* FROM demo_idempotency_keys k
                   JOIN demo_orders o ON o.id=k.order_id WHERE k.key=%s""", (idempotency_key,)
            ).fetchone()
            if prior:
                if prior["request_fingerprint"] != fingerprint:
                    return {"error": "idempotency_conflict"}
                return _order(prior)

        conn.execute("SELECT account_id,asset,available_amount FROM demo_balances WHERE account_id IN ('A','B') FOR UPDATE").fetchall()
        asset = "SAR" if side == "buy" else base
        funds = conn.execute(
            "SELECT available_amount FROM demo_balances WHERE account_id=%s AND asset=%s FOR UPDATE",
            (account, asset),
        ).fetchone()
        required = price * quantity if side == "buy" else quantity
        if not funds or funds["available_amount"] - _reserved(conn, account, asset) < required:
            return {"error": "insufficient_funds", "asset": asset}

        conn.execute(
            """INSERT INTO demo_orders(id,account_id,market,side,limit_price,quantity,remaining_quantity,status,created_at)
               VALUES (%s,%s,%s,%s,%s,%s,%s,'open',%s)""",
            (order_id, account, market, side, price, quantity, quantity, now),
        )
        condition = "limit_price <= %s" if side == "buy" else "limit_price >= %s"
        sort = "limit_price ASC, created_at ASC, id ASC" if side == "buy" else "limit_price DESC, created_at ASC, id ASC"
        makers = conn.execute(
            f"""SELECT * FROM demo_orders WHERE market=%s AND side=%s AND account_id<>%s
                AND status IN ('open','partially_filled') AND {condition}
                ORDER BY {sort} FOR UPDATE""",
            (market, "sell" if side == "buy" else "buy", account, price),
        ).fetchall()
        taker_remaining = quantity
        for maker in makers:
            if taker_remaining <= 0:
                break
            maker_remaining = maker["remaining_quantity"]
            qty = min(taker_remaining, maker_remaining)
            execution_price = maker["limit_price"]
            value = qty * execution_price
            buyer = account if side == "buy" else maker["account_id"]
            seller = maker["account_id"] if side == "buy" else account
            # Funds were reserved at order placement. Re-check live available balance under the same lock.
            buyer_sar = conn.execute("SELECT available_amount FROM demo_balances WHERE account_id=%s AND asset='SAR' FOR UPDATE", (buyer,)).fetchone()["available_amount"]
            seller_base = conn.execute("SELECT available_amount FROM demo_balances WHERE account_id=%s AND asset=%s FOR UPDATE", (seller, base)).fetchone()["available_amount"]
            # Exclude the maker/taker orders whose reserved funds are being consumed by this fill,
            # but preserve every other active order's reservation.
            current_orders = (order_id, maker["id"])
            buyer_free_sar = buyer_sar - _reserved(conn, buyer, "SAR", current_orders)
            seller_free_base = seller_base - _reserved(conn, seller, base, current_orders)
            if buyer_free_sar < value or seller_free_base < qty:
                continue
            conn.execute("UPDATE demo_balances SET available_amount=available_amount-%s,updated_at=now() WHERE account_id=%s AND asset='SAR'", (value,buyer))
            conn.execute("UPDATE demo_balances SET available_amount=available_amount+%s,updated_at=now() WHERE account_id=%s AND asset=%s", (qty,buyer,base))
            conn.execute("UPDATE demo_balances SET available_amount=available_amount-%s,updated_at=now() WHERE account_id=%s AND asset=%s", (qty,seller,base))
            conn.execute("UPDATE demo_balances SET available_amount=available_amount+%s,updated_at=now() WHERE account_id=%s AND asset='SAR'", (value,seller))
            new_maker_remaining = maker_remaining - qty
            maker_status = "filled" if new_maker_remaining == 0 else "partially_filled"
            conn.execute("UPDATE demo_orders SET remaining_quantity=%s,status=%s,updated_at=now() WHERE id=%s", (new_maker_remaining,maker_status,maker["id"]))
            taker_remaining -= qty
            conn.execute(
                """INSERT INTO demo_fills(id,market,maker_order_id,taker_order_id,buyer_account_id,seller_account_id,execution_price,quantity,simulated_value_sar,created_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (uuid4(),market,maker["id"],order_id,buyer,seller,execution_price,qty,value,now),
            )
        status = "filled" if taker_remaining == 0 else ("partially_filled" if taker_remaining < quantity else "open")
        conn.execute("UPDATE demo_orders SET remaining_quantity=%s,status=%s,updated_at=now() WHERE id=%s", (taker_remaining,status,order_id))
        if idempotency_key:
            conn.execute(
                "INSERT INTO demo_idempotency_keys(key,request_fingerprint,order_id) VALUES (%s,%s,%s)",
                (idempotency_key,fingerprint,order_id),
            )
        conn.execute(
            """INSERT INTO demo_audit_events(event_type,entity_type,entity_id,details)
               VALUES ('order_placed','order',%s,%s::jsonb)""",
            (str(order_id),json.dumps({"market":market,"side":side,"account":account,"status":status})),
        )
        row = conn.execute("SELECT * FROM demo_orders WHERE id=%s", (order_id,)).fetchone()
        return _order(row)


def audit():
    issues = []
    with _connect() as conn:
        bad = conn.execute(
            """SELECT o.id,o.quantity,o.remaining_quantity,
                 COALESCE((SELECT SUM(f.quantity) FROM demo_fills f WHERE f.maker_order_id=o.id OR f.taker_order_id=o.id),0) AS filled
               FROM demo_orders o"""
        ).fetchall()
        for row in bad:
            if abs(row["quantity"] - row["remaining_quantity"] - row["filled"]) > Decimal("0.00000001"):
                issues.append(f"order {row['id']}: quantity does not reconcile")
        self_trades = conn.execute("SELECT count(*) AS n FROM demo_fills WHERE buyer_account_id=seller_account_id OR maker_order_id=taker_order_id").fetchone()["n"]
        if self_trades:
            issues.append(f"{self_trades} invalid/self-trade fills")
        for asset, expected in INITIAL_TOTALS.items():
            actual = conn.execute("SELECT COALESCE(SUM(available_amount),0) AS total FROM demo_balances WHERE asset=%s", (asset,)).fetchone()["total"]
            if abs(actual - expected) > Decimal("0.000001"):
                issues.append(f"asset {asset}: balance conservation mismatch")
        negative = conn.execute("SELECT count(*) AS n FROM demo_balances WHERE available_amount<0").fetchone()["n"]
        if negative:
            issues.append("negative demo balances found")
        counts = conn.execute("SELECT (SELECT count(*) FROM demo_orders) AS orders,(SELECT count(*) FROM demo_fills) AS fills").fetchone()
    return {"mode":"simulation_only","valid":not issues,"orders_checked":counts["orders"],"fills_checked":counts["fills"],"issues":issues}

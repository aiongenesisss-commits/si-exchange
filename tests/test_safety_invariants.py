"""Regression tests for SI Exchange simulation safety invariants.

These tests exercise the in-memory demo backend only. They never connect to
wallets, public chains, payment systems, or real-money trading.
"""
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app import main as exchange


client = TestClient(exchange.app)


def setup_function():
    """Reset the process-local demo state before each test."""
    with exchange.lock:
        exchange.orders.clear()
        exchange.ledger.clear()
        exchange.idempotency_keys.clear()
        exchange.balances.clear()
        exchange.balances.update({
            account: {"SAR": 100000.0, **exchange.INITIAL_ASSETS.copy()}
            for account in ("A", "B")
        })


def payload(*, side="buy", account="A", price=250000, quantity=0.01):
    return {
        "market": "BTC/SAR",
        "side": side,
        "account": account,
        "price": price,
        "quantity": quantity,
    }


def test_idempotency_replay_returns_original_order_without_duplicate():
    first = client.post("/orders", json=payload(), headers={"Idempotency-Key": "safety-replay-001"})
    replay = client.post("/orders", json=payload(), headers={"Idempotency-Key": "safety-replay-001"})

    assert first.status_code == replay.status_code == 201
    assert replay.json()["id"] == first.json()["id"]
    assert len(client.get("/orders").json()) == 1
    assert client.get("/ledger").json() == []


def test_idempotency_key_reuse_with_different_payload_is_rejected():
    first = client.post("/orders", json=payload(), headers={"Idempotency-Key": "safety-conflict-001"})
    changed = client.post(
        "/orders",
        json=payload(quantity=0.02),
        headers={"Idempotency-Key": "safety-conflict-001"},
    )

    assert first.status_code == 201
    assert changed.status_code == 409
    assert len(client.get("/orders").json()) == 1


def test_open_orders_reserve_quote_and_base_assets():
    buy = client.post("/orders", json=payload(quantity=0.3))
    assert buy.status_code == 201
    available = client.get("/available-balances").json()["available_balances"]
    assert available["A"]["SAR"] == 25000.0

    overcommitted_buy = client.post("/orders", json=payload(quantity=0.11))
    assert overcommitted_buy.status_code == 409

    sell = client.post("/orders", json=payload(side="sell", account="B", quantity=0.2))
    assert sell.status_code == 201
    available = client.get("/available-balances").json()["available_balances"]
    assert available["B"]["BTC"] == 0.05

    overcommitted_sell = client.post(
        "/orders", json=payload(side="sell", account="B", quantity=0.06)
    )
    assert overcommitted_sell.status_code == 409


def test_one_taker_order_can_fill_against_multiple_resting_orders_partially():
    first_sell = client.post(
        "/orders", json=payload(side="sell", account="A", price=250000, quantity=0.01)
    )
    second_sell = client.post(
        "/orders", json=payload(side="sell", account="A", price=251000, quantity=0.02)
    )
    buy = client.post(
        "/orders", json=payload(side="buy", account="B", price=252000, quantity=0.025)
    )

    assert first_sell.status_code == second_sell.status_code == buy.status_code == 201
    assert buy.json()["status"] == "filled"
    assert client.get(f"/orders/{first_sell.json()['id']}").json()["status"] == "filled"
    resting_second = client.get(f"/orders/{second_sell.json()['id']}").json()
    assert resting_second["status"] == "partially_filled"
    assert abs(resting_second["remaining_quantity"] - 0.005) < 1e-10
    fills = client.get("/ledger").json()
    assert len(fills) == 2
    assert abs(sum(fill["quantity"] for fill in fills) - 0.025) < 1e-10
    assert client.get("/audit").json()["valid"] is True


def test_concurrent_orders_cannot_reserve_more_than_available_quote_balance():
    def place():
        return client.post("/orders", json=payload(account="A", quantity=0.3)).status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        statuses = list(pool.map(lambda _: place(), range(2)))

    assert sorted(statuses) == [201, 409]
    orders = client.get("/orders").json()
    assert len(orders) == 1
    assert client.get("/available-balances").json()["available_balances"]["A"]["SAR"] == 25000.0
    assert client.get("/audit").json()["valid"] is True


def test_audit_detects_balance_conservation_corruption():
    exchange.balances["A"]["SAR"] += 1.0

    result = client.get("/audit").json()

    assert result["valid"] is False
    assert any("balance conservation mismatch" in issue for issue in result["issues"])


def test_postgres_transaction_error_fails_closed_without_memory_fallback(monkeypatch):
    def fail_transaction(*_args, **_kwargs):
        raise RuntimeError("simulated database outage")

    monkeypatch.setenv("AION_STORAGE_BACKEND", "postgres")
    monkeypatch.setattr(exchange.postgres_store, "place_order", fail_transaction)

    response = client.post("/orders", json=payload())

    assert response.status_code == 503
    assert response.json()["detail"] == "PostgreSQL order transaction failed"
    assert exchange.orders == []
    assert exchange.ledger == []

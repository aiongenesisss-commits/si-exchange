from fastapi.testclient import TestClient

from app.main import app, balances, orders, ledger, idempotency_keys, INITIAL_ASSETS

client = TestClient(app)


def reset_state():
    orders.clear()
    ledger.clear()
    idempotency_keys.clear()
    for account in balances:
        balances[account].clear()
        balances[account].update({"SAR": 100000.0, **INITIAL_ASSETS.copy()})


def test_open_buy_orders_reserve_sar_and_reject_overcommitment():
    reset_state()
    first = client.post("/orders", json={
        "market": "BTC/SAR", "side": "buy", "account": "A",
        "price": 250000, "quantity": 0.3,
    })
    assert first.status_code == 201
    available = client.get("/available-balances").json()["available_balances"]
    assert available["A"]["SAR"] == 25000.0

    second = client.post("/orders", json={
        "market": "BTC/SAR", "side": "buy", "account": "A",
        "price": 250000, "quantity": 0.2,
    })
    assert second.status_code == 409
    assert "reservations" in second.json()["detail"].lower()
    assert len(orders) == 1


def test_open_sell_orders_reserve_base_asset_and_reject_overcommitment():
    reset_state()
    first = client.post("/orders", json={
        "market": "BTC/SAR", "side": "sell", "account": "A",
        "price": 250000, "quantity": 0.2,
    })
    assert first.status_code == 201
    available = client.get("/available-balances").json()["available_balances"]
    assert available["A"]["BTC"] == 0.05

    second = client.post("/orders", json={
        "market": "BTC/SAR", "side": "sell", "account": "A",
        "price": 250000, "quantity": 0.1,
    })
    assert second.status_code == 409
    assert len(orders) == 1


def test_filled_order_releases_reservation_and_conserves_balances():
    reset_state()
    sell = client.post("/orders", json={
        "market": "SOL/SAR", "side": "sell", "account": "A",
        "price": 600, "quantity": 1,
    })
    buy = client.post("/orders", json={
        "market": "SOL/SAR", "side": "buy", "account": "B",
        "price": 600, "quantity": 1,
    })
    assert sell.status_code == 201 and buy.status_code == 201
    available = client.get("/available-balances").json()["available_balances"]
    assert available["A"]["SOL"] == 19.0
    assert available["B"]["SOL"] == 21.0
    assert client.get("/audit").json()["valid"] is True

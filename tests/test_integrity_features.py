from fastapi.testclient import TestClient

from app.main import app, balances, idempotency_keys, ledger, orders

client = TestClient(app)


def reset_state():
    orders.clear()
    ledger.clear()
    idempotency_keys.clear()
    for account in balances:
        balances[account].update({"SAR": 100000.0, "BTC": 0.25, "ETH": 2.0})


def test_audit_starts_valid_and_preserves_total_balances():
    reset_state()
    response = client.get("/audit")
    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is True
    assert body["orders_checked"] == 0
    assert body["fills_checked"] == 0


def test_idempotency_key_does_not_create_duplicate_order():
    reset_state()
    payload = {
        "market": "BTC/SAR",
        "side": "buy",
        "account": "A",
        "price": 200000,
        "quantity": 0.001,
    }
    first = client.post("/orders", json=payload, headers={"Idempotency-Key": "test-order-1"})
    second = client.post("/orders", json=payload, headers={"Idempotency-Key": "test-order-1"})
    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
    assert len(orders) == 1


def test_reusing_idempotency_key_with_different_payload_is_rejected():
    reset_state()
    headers = {"Idempotency-Key": "same-key"}
    first = client.post(
        "/orders",
        json={"market": "BTC/SAR", "side": "buy", "account": "A", "price": 200000, "quantity": 0.001},
        headers=headers,
    )
    second = client.post(
        "/orders",
        json={"market": "BTC/SAR", "side": "buy", "account": "A", "price": 200000, "quantity": 0.002},
        headers=headers,
    )
    assert first.status_code == 201
    assert second.status_code == 409
    assert len(orders) == 1


def test_audit_reconciles_a_simulated_fill():
    reset_state()
    sell = client.post(
        "/orders",
        json={"market": "BTC/SAR", "side": "sell", "account": "A", "price": 200000, "quantity": 0.01},
    )
    buy = client.post(
        "/orders",
        json={"market": "BTC/SAR", "side": "buy", "account": "B", "price": 200000, "quantity": 0.01},
    )
    assert sell.status_code == 201
    assert buy.status_code == 201
    assert buy.json()["status"] == "filled"
    audit = client.get("/audit")
    assert audit.status_code == 200
    assert audit.json()["valid"] is True
    assert audit.json()["fills_checked"] == 1
    fill = client.get("/ledger").json()[0]
    assert fill["maker_order_id"] == sell.json()["id"]
    assert fill["taker_order_id"] == buy.json()["id"]
    assert fill["buyer_account"] == "B"
    assert fill["seller_account"] == "A"

from fastapi.testclient import TestClient

from app.main import app, balances, idempotency_keys, ledger, orders

client = TestClient(app)


def reset_demo_state():
    orders.clear()
    ledger.clear()
    idempotency_keys.clear()
    for account in ("A", "B"):
        balances[account].update({"SAR": 100000.0, "BTC": 0.25, "ETH": 2.0})


def test_idempotency_key_replay_does_not_create_duplicate_order():
    reset_demo_state()
    payload = {"market": "BTC/SAR", "side": "sell", "account": "A", "price": 240000, "quantity": 0.01}
    first = client.post("/orders", json=payload, headers={"Idempotency-Key": "sell-001"})
    replay = client.post("/orders", json=payload, headers={"Idempotency-Key": "sell-001"})
    assert first.status_code == 201
    assert replay.status_code == 201
    assert first.json()["id"] == replay.json()["id"]
    assert len(client.get("/orders").json()) == 1


def test_idempotency_key_rejects_different_payload():
    reset_demo_state()
    headers = {"Idempotency-Key": "same-key"}
    first = client.post("/orders", json={"market": "BTC/SAR", "side": "sell", "account": "A", "price": 240000, "quantity": 0.01}, headers=headers)
    second = client.post("/orders", json={"market": "BTC/SAR", "side": "sell", "account": "A", "price": 240000, "quantity": 0.02}, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 409
    assert len(client.get("/orders").json()) == 1


def test_fill_ledger_has_both_orders_and_audit_reconciles():
    reset_demo_state()
    sell = client.post("/orders", json={"market": "BTC/SAR", "side": "sell", "account": "A", "price": 240000, "quantity": 0.01})
    buy = client.post("/orders", json={"market": "BTC/SAR", "side": "buy", "account": "B", "price": 250000, "quantity": 0.01})
    assert sell.status_code == 201
    assert buy.status_code == 201
    fill = client.get("/ledger").json()[0]
    assert fill["maker_order_id"] == sell.json()["id"]
    assert fill["taker_order_id"] == buy.json()["id"]
    assert fill["buyer_account"] == "B"
    assert fill["seller_account"] == "A"
    audit = client.get("/audit").json()
    assert audit["valid"] is True
    assert audit["orders_checked"] == 2
    assert audit["fills_checked"] == 1
    assert audit["issues"] == []


def test_audit_passes_for_empty_demo_state():
    reset_demo_state()
    audit = client.get("/audit")
    assert audit.status_code == 200
    assert audit.json()["valid"] is True

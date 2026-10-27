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


def test_same_idempotency_key_and_payload_returns_original_order():
    reset_state()
    payload = {
        "market": "BTC/SAR",
        "side": "buy",
        "account": "A",
        "price": 100000,
        "quantity": 0.1,
    }
    first = client.post("/orders", json=payload, headers={"Idempotency-Key": "retry-test-001"})
    replay = client.post("/orders", json=payload, headers={"Idempotency-Key": "retry-test-001"})

    assert first.status_code == 201
    assert replay.status_code == 201
    assert replay.json()["id"] == first.json()["id"]
    assert len(orders) == 1


def test_reusing_idempotency_key_with_different_payload_returns_conflict():
    reset_state()
    headers = {"Idempotency-Key": "retry-test-002"}
    first = client.post("/orders", json={
        "market": "BTC/SAR", "side": "buy", "account": "A",
        "price": 100000, "quantity": 0.1,
    }, headers=headers)
    second = client.post("/orders", json={
        "market": "BTC/SAR", "side": "buy", "account": "A",
        "price": 100001, "quantity": 0.1,
    }, headers=headers)

    assert first.status_code == 201
    assert second.status_code == 409
    assert len(orders) == 1


def test_idempotency_key_length_limit_is_enforced():
    reset_state()
    response = client.post("/orders", json={
        "market": "BTC/SAR", "side": "buy", "account": "A",
        "price": 100000, "quantity": 0.1,
    }, headers={"Idempotency-Key": "x" * 201})
    assert response.status_code == 400
    assert orders == []

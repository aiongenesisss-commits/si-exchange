"""Authentication and account-isolation regression tests."""
import json
import os

from fastapi.testclient import TestClient

from app.main import app, orders, ledger, balances, idempotency_keys, INITIAL_ASSETS

client = TestClient(app)


def setup_function():
    orders.clear()
    ledger.clear()
    idempotency_keys.clear()
    balances.clear()
    balances.update({
        "A": {"SAR": 100000.0, **INITIAL_ASSETS.copy()},
        "B": {"SAR": 100000.0, **INITIAL_ASSETS.copy()},
    })


def auth_env(monkeypatch):
    monkeypatch.setenv("AION_AUTH_REQUIRED", "true")
    monkeypatch.setenv("AION_DEMO_SUBJECT_ACCOUNT_MAP", json.dumps({"subject-a": "A", "subject-b": "B"}))
    monkeypatch.setenv("AION_OIDC_JWKS_URL", "https://issuer.example/.well-known/jwks.json")
    monkeypatch.setenv("AION_OIDC_ISSUER", "https://issuer.example/")
    monkeypatch.setenv("AION_OIDC_AUDIENCE", "si-exchange-demo")


def install_claim_verifier(monkeypatch):
    import app.auth as auth
    def fake_verify(token):
        if token == "valid-a":
            return {"sub": "subject-a", "iss": "https://issuer.example/", "aud": "si-exchange-demo"}
        if token == "valid-b":
            return {"sub": "subject-b", "iss": "https://issuer.example/", "aud": "si-exchange-demo"}
        raise auth.AuthenticationError("invalid token")
    monkeypatch.setattr(auth, "verify_access_token", fake_verify)


def test_private_api_requires_verified_bearer_token(monkeypatch):
    import app.main as main
    auth_env(monkeypatch)
    install_claim_verifier(monkeypatch)
    monkeypatch.setattr(main, "_is_managed_deployment", lambda: False)
    assert client.get("/balances").status_code == 401
    assert client.get("/balances", headers={"Authorization": "Bearer forged"}).status_code == 401


def test_account_a_cannot_read_account_b_or_submit_orders_for_b(monkeypatch):
    import app.main as main
    auth_env(monkeypatch)
    install_claim_verifier(monkeypatch)
    monkeypatch.setattr(main, "_is_managed_deployment", lambda: False)
    headers = {"Authorization": "Bearer valid-a"}
    balances_response = client.get("/balances", headers=headers)
    assert balances_response.status_code == 200
    assert set(balances_response.json()["balances"]) == {"A"}
    assert client.get("/available-balances", headers=headers).json()["available_balances"].keys() == {"A"}
    assert client.get("/orders", headers=headers).json() == []
    placed = client.post("/orders", headers=headers, json={
        "market": "AION/SAR", "side": "sell", "account": "B", "price": 0.10, "quantity": 1
    })
    assert placed.status_code == 201
    assert placed.json()["account"] == "A"
    assert client.get("/orders", headers={"Authorization": "Bearer valid-b"}).json() == []
    assert client.get("/ledger", headers=headers).json() == []
    assert client.get("/audit", headers=headers).status_code == 200


def test_account_b_cannot_fetch_account_a_order_detail(monkeypatch):
    import app.main as main
    auth_env(monkeypatch)
    install_claim_verifier(monkeypatch)
    monkeypatch.setattr(main, "_is_managed_deployment", lambda: False)
    placed = client.post("/orders", headers={"Authorization": "Bearer valid-a"}, json={
        "market": "BTC/SAR", "side": "sell", "account": "A", "price": 250000, "quantity": 0.01
    })
    assert placed.status_code == 201
    response = client.get(f"/orders/{placed.json()['id']}", headers={"Authorization": "Bearer valid-b"})
    assert response.status_code == 404


def test_idempotency_is_scoped_to_authenticated_account(monkeypatch):
    import app.main as main
    auth_env(monkeypatch)
    install_claim_verifier(monkeypatch)
    monkeypatch.setattr(main, "_is_managed_deployment", lambda: False)
    payload = {"market": "AION/SAR", "side": "sell", "account": "A", "price": 0.10, "quantity": 1}
    first = client.post("/orders", headers={"Authorization": "Bearer valid-a", "Idempotency-Key": "same"}, json=payload)
    second = client.post("/orders", headers={"Authorization": "Bearer valid-b", "Idempotency-Key": "same"}, json={**payload, "account": "B"})
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    assert first.json()["account"] == "A" and second.json()["account"] == "B"

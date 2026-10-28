from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _clear_managed_env(monkeypatch):
    for name in ("VERCEL", "RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "AION_ACCESS_MODE"):
        monkeypatch.delenv(name, raising=False)


def test_private_demo_routes_are_locked_on_managed_deployments(monkeypatch):
    _clear_managed_env(monkeypatch)
    monkeypatch.setenv("VERCEL", "1")

    for path in ("/balances", "/available-balances", "/orders", "/ledger", "/audit", "/orders/not-real"):
        response = client.get(path)
        assert response.status_code == 503, (path, response.text)
        assert response.json()["code"] == "private_api_locked"
        assert response.json()["simulation_only"] is True

    response = client.post(
        "/orders",
        json={"market": "BTC/SAR", "side": "buy", "account": "A", "price": 250000, "quantity": 0.001},
    )
    assert response.status_code == 503
    assert response.json()["code"] == "private_api_locked"


def test_private_demo_routes_can_be_explicitly_locked_in_local_mode(monkeypatch):
    _clear_managed_env(monkeypatch)
    monkeypatch.setenv("AION_ACCESS_MODE", "locked")

    response = client.get("/balances")
    assert response.status_code == 503
    assert response.json()["code"] == "private_api_locked"


def test_public_read_only_routes_remain_available_when_private_routes_are_locked(monkeypatch):
    _clear_managed_env(monkeypatch)
    monkeypatch.setenv("RAILWAY_ENVIRONMENT", "production")

    # These routes are present on the PR's base branch; avoid depending on
    # market-data-status until its separate feature PR is merged.
    assert client.get("/health").status_code == 200
    assert client.get("/markets").status_code == 200
    assert client.get("/networks").status_code == 200
    assert client.get("/online-manifest").status_code == 200

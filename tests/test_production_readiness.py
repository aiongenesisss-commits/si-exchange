from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_production_readiness_never_claims_real_financial_readiness(monkeypatch):
    for name in ("VERCEL", "RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "DATABASE_URL", "AION_STORAGE_BACKEND"):
        monkeypatch.delenv(name, raising=False)

    response = client.get("/production-readiness")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "not_production_ready"
    assert body["mode"] == "simulation_only"
    assert body["checks"]["verified_authentication"] is False
    assert body["checks"]["per_user_account_isolation"] is False
    assert body["checks"]["real_deposits_withdrawals_custody"] is False
    assert body["checks"]["live_trading"] is False
    assert "verified_authentication_not_implemented" in body["blockers"]
    assert "per_user_account_isolation_not_implemented" in body["blockers"]
    assert "persistent_postgresql_not_configured" in body["blockers"]


def test_production_readiness_reports_configuration_without_exposing_database_url(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("AION_STORAGE_BACKEND", "postgres")
    monkeypatch.setenv("DATABASE_URL", "postgresql://secret-user:secret-password@example.invalid/db")

    body = client.get("/production-readiness").json()
    assert body["checks"]["managed_deployment_detected"] is True
    assert body["checks"]["persistent_database_configured"] is True
    assert body["status"] == "not_production_ready"
    serialized = str(body)
    assert "secret-password" not in serialized
    assert "secret-user" not in serialized

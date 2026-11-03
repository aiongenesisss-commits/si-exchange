from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
REPO_ROOT = Path(__file__).resolve().parents[1]


def _clear_managed_env(monkeypatch):
    for name in ("VERCEL", "RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "AION_ACCESS_MODE"):
        monkeypatch.delenv(name, raising=False)


def test_public_health_contract_stays_available_when_private_apis_are_locked(monkeypatch):
    _clear_managed_env(monkeypatch)
    monkeypatch.setenv("VERCEL", "1")

    public_paths = (
        "/health",
        "/ready",
        "/api",
        "/online-manifest",
        "/markets",
        "/networks",
        "/production-readiness",
    )
    for path in public_paths:
        response = client.get(path)
        assert response.status_code == 200, (path, response.text)

    private_paths = ("/balances", "/available-balances", "/orders", "/ledger", "/audit")
    for path in private_paths:
        response = client.get(path)
        assert response.status_code == 503, (path, response.text)
        assert response.json()["code"] == "private_api_locked"


def test_github_actions_health_monitors_probe_public_routes_only():
    workflow_paths = (
        REPO_ROOT / ".github" / "workflows" / "public-service-health.yml",
        REPO_ROOT / ".github" / "workflows" / "online-smoke.yml",
    )
    private_route_tokens = ("/balances", "/available-balances", "/orders", "/ledger", "/audit")

    for workflow_path in workflow_paths:
        content = workflow_path.read_text(encoding="utf-8")
        for private_path in private_route_tokens:
            assert private_path not in content, (workflow_path.name, private_path)

    public_health = workflow_paths[0].read_text(encoding="utf-8")
    online_smoke = workflow_paths[1].read_text(encoding="utf-8")
    for public_path in ("/health", "/ready", "/api", "/online-manifest", "/markets", "/networks"):
        assert public_path in public_health
        assert public_path in online_smoke

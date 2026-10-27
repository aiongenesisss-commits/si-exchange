"""Opt-in real PostgreSQL integration tests; skipped unless TEST_DATABASE_URL is provided."""
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not DATABASE_URL, reason="TEST_DATABASE_URL not configured")


def _prepare_database():
    import psycopg
    migration = Path(__file__).resolve().parents[1] / "migrations" / "001_initial_schema.sql"
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(migration.read_text())
        # Dedicated CI database only: clear previous test run, then allow app to seed demo accounts.
        conn.execute("TRUNCATE demo_audit_events,demo_idempotency_keys,demo_fills,demo_orders,demo_balances,demo_accounts RESTART IDENTITY CASCADE")


def test_postgres_orders_balances_and_idempotency_survive_client_restart(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", DATABASE_URL)
    monkeypatch.setenv("AION_STORAGE_BACKEND", "postgres")
    _prepare_database()
    from app.main import app

    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200 and health.json()["storage"] == "postgres"
        sell = client.post("/orders", headers={"Idempotency-Key": "persist-sell-001"}, json={
            "market": "BTC/SAR", "side": "sell", "account": "A", "price": 250000, "quantity": 0.01
        })
        assert sell.status_code == 201, sell.text
        sell_id = sell.json()["id"]
        repeated = client.post("/orders", headers={"Idempotency-Key": "persist-sell-001"}, json={
            "market": "BTC/SAR", "side": "sell", "account": "A", "price": 250000, "quantity": 0.01
        })
        assert repeated.status_code == 201 and repeated.json()["id"] == sell_id

    # A fresh TestClient simulates an application process restart while using the same database.
    with TestClient(app) as client:
        persisted = client.get(f"/orders/{sell_id}")
        assert persisted.status_code == 200 and persisted.json()["status"] == "open"
        buy = client.post("/orders", headers={"Idempotency-Key": "persist-buy-001"}, json={
            "market": "BTC/SAR", "side": "buy", "account": "B", "price": 250000, "quantity": 0.01
        })
        assert buy.status_code == 201 and buy.json()["status"] == "filled"
        assert len(client.get("/ledger").json()) == 1
        audit = client.get("/audit")
        assert audit.status_code == 200 and audit.json()["valid"], audit.text

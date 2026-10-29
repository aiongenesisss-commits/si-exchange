"""Real Redis integration tests, enabled only when REDIS_URL points to an isolated test service."""
import json
import os
from uuid import uuid4

import pytest

from app import redis_store

REDIS_URL = os.getenv("REDIS_URL")
pytestmark = pytest.mark.skipif(not REDIS_URL, reason="REDIS_URL not configured")


def test_real_redis_round_trip_survives_new_client(monkeypatch):
    monkeypatch.setenv("REDIS_URL", REDIS_URL)
    client = redis_store._client()
    redis_store.check_connection()
    key = f"{redis_store.STATE_KEY}:ci:{uuid4()}"
    state = {
        "balances": {"A": {"SAR": 100000.0}, "B": {"SAR": 100000.0}},
        "orders": [{"id": "demo-order", "status": "open"}],
        "ledger": [{"id": "demo-fill", "quantity": 0.01}],
        "idempotency_keys": {"demo-key": {"fingerprint": "test", "order_id": "demo-order"}},
    }
    try:
        payload = json.dumps(state, separators=(",", ":"), allow_nan=False)
        client.set(key, payload)
        # A newly constructed client models reconnect/application restart.
        restarted_client = redis_store._client()
        assert json.loads(restarted_client.get(key)) == state
    finally:
        client.delete(key)


def test_real_redis_rejects_incomplete_state(monkeypatch):
    monkeypatch.setenv("REDIS_URL", REDIS_URL)
    client = redis_store._client()
    key = f"{redis_store.STATE_KEY}:ci:incomplete:{uuid4()}"
    try:
        client.set(key, '{"balances": {}}')
        raw = client.get(key)
        state = json.loads(raw)
        required = {"balances", "orders", "ledger", "idempotency_keys"}
        assert not required.issubset(state)
    finally:
        client.delete(key)

"""Real Redis integration tests, enabled only when REDIS_URL points to an isolated test service."""
import os

import pytest

from app import redis_store

REDIS_URL = os.getenv("REDIS_URL")
pytestmark = pytest.mark.skipif(not REDIS_URL, reason="REDIS_URL not configured")


def test_real_redis_round_trip_survives_new_client(monkeypatch):
    monkeypatch.setenv("REDIS_URL", REDIS_URL)
    client = redis_store._client()
    redis_store.check_connection()
    client.delete(redis_store.STATE_KEY)
    state = {
        "balances": {"A": {"SAR": 100000.0}, "B": {"SAR": 100000.0}},
        "orders": [{"id": "demo-order", "status": "open"}],
        "ledger": [{"id": "demo-fill", "quantity": 0.01}],
        "idempotency_keys": {"demo-key": {"fingerprint": "test", "order_id": "demo-order"}},
    }
    try:
        redis_store.save_state(state)
        # A newly constructed client models reconnect/application restart.
        monkeypatch.setattr(redis_store, "_client", lambda: redis_store.redis.Redis.from_url(
            REDIS_URL, decode_responses=True, socket_connect_timeout=3, socket_timeout=3
        ))
        assert redis_store.load_state() == state
    finally:
        client.delete(redis_store.STATE_KEY)


def test_real_redis_rejects_incomplete_state(monkeypatch):
    monkeypatch.setenv("REDIS_URL", REDIS_URL)
    client = redis_store._client()
    client.delete(redis_store.STATE_KEY)
    try:
        client.set(redis_store.STATE_KEY, '{"balances": {}}')
        with pytest.raises(RuntimeError, match="missing required fields"):
            redis_store.load_state()
    finally:
        client.delete(redis_store.STATE_KEY)

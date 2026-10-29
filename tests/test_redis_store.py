import json
import os
import uuid
from urllib.parse import urlparse

from app import redis_store


class FakeRedis:
    def __init__(self):
        self.values = {}

    def ping(self):
        return True

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value
        return True


def test_redis_state_round_trip_is_atomic_json(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(redis_store, "_client", lambda: fake)
    state = {
        "balances": {"A": {"SAR": 100000.0}, "B": {"SAR": 100000.0}},
        "orders": [{"id": "order-1", "status": "open"}],
        "ledger": [],
        "idempotency_keys": {"key-1": {"fingerprint": "abc", "order_id": "order-1"}},
    }
    redis_store.check_connection()
    redis_store.save_state(state)
    assert json.loads(fake.values[redis_store.STATE_KEY]) == state
    assert redis_store.load_state() == state


def test_redis_load_rejects_incomplete_saved_state(monkeypatch):
    fake = FakeRedis()
    fake.values[redis_store.STATE_KEY] = '{"balances": {}}'
    monkeypatch.setattr(redis_store, "_client", lambda: fake)
    try:
        redis_store.load_state()
    except RuntimeError as exc:
        assert "missing required fields" in str(exc)
    else:
        raise AssertionError("Incomplete Redis state must fail closed")


def test_real_redis_connection_and_round_trip_when_configured(monkeypatch):
    """Use only the ephemeral local CI Redis and a unique test key."""
    test_url = os.getenv("TEST_REDIS_URL", "").strip()
    if not test_url:
        import pytest
        pytest.skip("TEST_REDIS_URL is not configured; no live Redis test attempted")

    parsed_url = urlparse(test_url)
    if parsed_url.hostname not in {"localhost", "127.0.0.1", "::1"} or parsed_url.path != "/15":
        raise AssertionError(
            "Refusing live Redis test: TEST_REDIS_URL must target loopback host and database /15"
        )

    client = redis_store.redis.Redis.from_url(
        test_url,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
    )
    protected_state_key = redis_store.STATE_KEY
    test_key = f"si_exchange:test:redis_integration:{uuid.uuid4().hex}"
    assert test_key != protected_state_key
    original_state = client.get(protected_state_key)

    # Redirect save/load to a unique disposable key. Never delete the app state key.
    monkeypatch.setattr(redis_store, "STATE_KEY", test_key)
    monkeypatch.setattr(redis_store, "_client", lambda: client)
    state = {
        "balances": {"TEST-A": {"SAR": 123.45}},
        "orders": [{"id": "redis-integration-test", "status": "open"}],
        "ledger": [],
        "idempotency_keys": {
            "redis-integration-test-key": {
                "fingerprint": "test",
                "order_id": "redis-integration-test",
            }
        },
    }
    try:
        redis_store.check_connection()
        redis_store.save_state(state)
        assert redis_store.load_state() == state
        assert client.get(protected_state_key) == original_state
    finally:
        # Cleanup is restricted to this run's random test key.
        client.delete(test_key)
        client.close()

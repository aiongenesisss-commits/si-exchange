import json
import os
import uuid

import pytest
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

    def delete(self, key):
        return int(self.values.pop(key, None) is not None)


def _new_test_key():
    return f"si_exchange:test:{uuid.uuid4().hex}:state"


def _safe_delete_test_key(client, test_key, application_state_key):
    """Delete only a non-empty, per-run test key; never delete app state."""
    if not test_key or test_key == application_state_key:
        raise RuntimeError("Refusing to delete the application state key")
    if not test_key.startswith("si_exchange:test:"):
        raise RuntimeError("Refusing to delete a key outside the test namespace")
    return client.delete(test_key)


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
    with pytest.raises(RuntimeError, match="missing required fields"):
        redis_store.load_state()


def test_test_cleanup_refuses_application_state_key_and_preserves_data():
    fake = FakeRedis()
    application_key = redis_store.STATE_KEY
    sentinel = '{"balances":{"production-like":"untouched"}}'
    fake.set(application_key, sentinel)

    with pytest.raises(RuntimeError, match="application state key"):
        _safe_delete_test_key(fake, application_key, application_key)

    assert fake.get(application_key) == sentinel


def test_test_keys_are_unique_and_isolated_between_runs():
    first_key = _new_test_key()
    second_key = _new_test_key()
    assert first_key != second_key
    assert first_key.startswith("si_exchange:test:")
    assert second_key.startswith("si_exchange:test:")

    fake = FakeRedis()
    fake.set(first_key, '{"run":1}')
    fake.set(second_key, '{"run":2}')
    assert fake.get(first_key) == '{"run":1}'
    assert fake.get(second_key) == '{"run":2}'

    _safe_delete_test_key(fake, first_key, redis_store.STATE_KEY)
    assert fake.get(first_key) is None
    assert fake.get(second_key) == '{"run":2}'


def test_real_redis_connection_and_round_trip_when_configured(monkeypatch):
    """Exercise a real Redis server only when a dedicated test URL is supplied."""
    test_url = os.getenv("TEST_REDIS_URL", "").strip()
    if not test_url:
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
    application_state_key = redis_store.STATE_KEY
    application_state_before = client.get(application_state_key)
    test_key = _new_test_key()
    assert test_key != application_state_key
    # Route store operations to this run's random key, never to the app key.
    monkeypatch.setattr(redis_store, "STATE_KEY", test_key)
    monkeypatch.setattr(redis_store, "_client", lambda: client)
    state = {
        "balances": {"TEST-A": {"SAR": 123.45}},
        "orders": [{"id": f"redis-integration-{uuid.uuid4().hex}", "status": "open"}],
        "ledger": [],
        "idempotency_keys": {},
    }
    try:
        redis_store.check_connection()
        redis_store.save_state(state)
        assert redis_store.load_state() == state
        assert client.get(application_state_key) == application_state_before
    finally:
        _safe_delete_test_key(client, test_key, application_state_key)
        client.close()

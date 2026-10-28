import json

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

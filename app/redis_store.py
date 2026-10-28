"""Redis-backed persistence for simulation-only exchange state.

The Redis endpoint must be private and authenticated. This module stores only demo
balances, orders, fills, and idempotency records; never keys or real assets.
"""
import json
import os
import redis

STATE_KEY = "si_exchange:demo_state:v1"


def _client():
    url = os.getenv("REDIS_URL", "").strip()
    if not url:
        raise RuntimeError("REDIS_URL is required when AION_STORAGE_BACKEND=redis")
    return redis.Redis.from_url(url, decode_responses=True, socket_connect_timeout=3, socket_timeout=3)


def check_connection():
    if not _client().ping():
        raise RuntimeError("Redis ping failed")


def load_state():
    raw = _client().get(STATE_KEY)
    if raw is None:
        return None
    state = json.loads(raw)
    required = {"balances", "orders", "ledger", "idempotency_keys"}
    if not required.issubset(state):
        raise RuntimeError("Stored Redis state is missing required fields")
    return state


def save_state(state):
    # One atomic Redis SET avoids partially-written JSON snapshots.
    payload = json.dumps(state, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    _client().set(STATE_KEY, payload)

"""Real PostgreSQL persistence regression tests.

These tests run only against TEST_DATABASE_URL and refuse databases whose
name does not end in "_test". They never use production credentials or funds.
"""
from pathlib import Path
from urllib.parse import urlparse

import pytest
import psycopg

from app import postgres_store
from app.main import OrderRequest

TEST_DATABASE_URL = __import__("os").getenv("TEST_DATABASE_URL")


def _test_database_url():
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL is not configured")
    database_name = urlparse(TEST_DATABASE_URL).path.lstrip("/")
    if not database_name.endswith("_test"):
        pytest.fail(
            "Refusing PostgreSQL integration tests: TEST_DATABASE_URL database "
            "name must end with '_test'."
        )
    return TEST_DATABASE_URL


@pytest.fixture
def postgres_demo(monkeypatch):
    database_url = _test_database_url()
    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("AION_STORAGE_BACKEND", "postgres")

    migration = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "001_initial_schema.sql"
    ).read_text(encoding="utf-8")

    with psycopg.connect(database_url, autocommit=True) as conn:
        conn.execute(migration)
        conn.execute(
            """
            TRUNCATE TABLE
                demo_fills,
                demo_idempotency_keys,
                demo_orders,
                demo_audit_events,
                demo_balances,
                demo_accounts
            RESTART IDENTITY CASCADE
            """
        )

    postgres_store.initialize_demo_accounts()
    return postgres_store


def _order(*, side, account, price, quantity):
    return OrderRequest(
        market="BTC/SAR",
        side=side,
        account=account,
        price=price,
        quantity=quantity,
    )


def test_orders_and_balances_survive_reinitialization(postgres_demo):
    created = postgres_demo.place_order(
        _order(side="buy", account="A", price=200000, quantity=0.01),
        idempotency_key="postgres-persist-001",
    )
    assert created["status"] == "open"

    # A fresh DB connection observes the order and reservation; startup seeding
    # must not reset balances or erase durable records.
    postgres_demo.check_connection()
    postgres_demo.initialize_demo_accounts()

    orders = postgres_demo.list_orders()
    assert len(orders) == 1
    assert orders[0]["id"] == created["id"]
    assert orders[0]["status"] == "open"

    balances = postgres_demo.balances()["balances"]
    available = postgres_demo.available_balances()["available_balances"]
    assert balances["A"]["SAR"] == 100000.0
    assert available["A"]["SAR"] == 98000.0
    assert postgres_demo.audit()["valid"] is True


def test_postgres_fill_ledger_and_idempotency_are_durable(postgres_demo):
    maker = postgres_demo.place_order(
        _order(side="sell", account="B", price=240000, quantity=0.01)
    )
    taker = postgres_demo.place_order(
        _order(side="buy", account="A", price=250000, quantity=0.01),
        idempotency_key="postgres-fill-001",
    )
    replay = postgres_demo.place_order(
        _order(side="buy", account="A", price=250000, quantity=0.01),
        idempotency_key="postgres-fill-001",
    )

    assert maker["status"] == "filled"
    assert taker["status"] == "filled"
    assert replay["id"] == taker["id"]
    assert len(postgres_demo.list_orders()) == 2
    fills = postgres_demo.list_fills()
    assert len(fills) == 1
    assert fills[0]["maker_order_id"] == maker["id"]
    assert fills[0]["taker_order_id"] == taker["id"]
    assert postgres_demo.audit()["valid"] is True

    # Simulate process reinitialization: seeded demo accounts are insert-only.
    postgres_demo.initialize_demo_accounts()
    assert len(postgres_demo.list_fills()) == 1
    assert postgres_demo.audit()["valid"] is True

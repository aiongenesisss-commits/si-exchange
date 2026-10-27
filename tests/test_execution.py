import pytest

from app.execution import InProcessSandboxAdapter, build_execution_adapter


def sample(adapter, key="request-1"):
    return adapter.submit_order(
        market="BTC/SAR", side="buy", price="250000.00",
        quantity="0.001", idempotency_key=key,
    )


def test_default_mode_is_local_simulation(monkeypatch):
    monkeypatch.delenv("EXECUTION_MODE", raising=False)
    monkeypatch.delenv("REAL_TRADING_ENABLED", raising=False)
    adapter = build_execution_adapter()
    assert isinstance(adapter, InProcessSandboxAdapter)
    assert adapter.mode == "simulation_only"


def test_sandbox_order_can_be_read_and_cancelled():
    adapter = InProcessSandboxAdapter()
    order = sample(adapter)
    assert adapter.get_order(order.order_id) == order
    cancelled = adapter.cancel_order(order.order_id)
    assert cancelled.status == "cancelled"
    assert adapter.cancel_order(order.order_id) == cancelled


def test_idempotency_replays_same_order():
    adapter = InProcessSandboxAdapter()
    first = sample(adapter, "same-key")
    second = sample(adapter, "same-key")
    assert second.order_id == first.order_id


def test_idempotency_key_cannot_be_reused_for_different_order():
    adapter = InProcessSandboxAdapter()
    sample(adapter, "same-key")
    with pytest.raises(ValueError, match="different order"):
        adapter.submit_order(
            market="ETH/SAR", side="buy", price="9000",
            quantity="1", idempotency_key="same-key",
        )


@pytest.mark.parametrize("mode", ["live", "production", "typo", ""])
def test_unknown_and_live_modes_fail_closed(mode):
    with pytest.raises(RuntimeError):
        build_execution_adapter(mode)


def test_live_flag_cannot_enable_unimplemented_execution(monkeypatch):
    monkeypatch.setenv("REAL_TRADING_ENABLED", "true")
    with pytest.raises(RuntimeError, match="not implemented"):
        build_execution_adapter("sandbox")


@pytest.mark.parametrize("price,quantity", [("0", "1"), ("1", "-1"), ("NaN", "1"), ("Infinity", "2")])
def test_invalid_amounts_rejected(price, quantity):
    adapter = InProcessSandboxAdapter()
    with pytest.raises(ValueError):
        adapter.submit_order(
            market="BTC/SAR", side="buy", price=price, quantity=quantity,
            idempotency_key="invalid",
        )


def test_unknown_order_is_not_found():
    adapter = InProcessSandboxAdapter()
    with pytest.raises(KeyError, match="unknown sandbox order"):
        adapter.get_order("not-a-real-order")

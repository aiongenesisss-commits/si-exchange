import json
from urllib.parse import parse_qs, urlparse

import pytest

from app.binance_testnet import BinanceSpotTestnetAdapter, TESTNET_BASE_URL
from app.execution import InProcessSandboxAdapter, build_execution_adapter


class FakeResponse:
    def __init__(self, data):
        self.payload = json.dumps(data).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_default_mode_is_local_simulation(monkeypatch):
    monkeypatch.delenv("EXECUTION_MODE", raising=False)
    monkeypatch.delenv("REAL_TRADING_ENABLED", raising=False)
    adapter = build_execution_adapter()
    assert isinstance(adapter, InProcessSandboxAdapter)
    assert adapter.mode == "simulation_only"


@pytest.mark.parametrize("mode", ["live", "production", "typo", ""])
def test_unknown_modes_fail_closed(mode):
    with pytest.raises(RuntimeError):
        build_execution_adapter(mode)


def test_live_flag_cannot_enable_any_execution(monkeypatch):
    monkeypatch.setenv("REAL_TRADING_ENABLED", "true")
    with pytest.raises(RuntimeError, match="not implemented"):
        build_execution_adapter("simulation")


def test_local_sandbox_order_can_be_read_and_cancelled():
    adapter = InProcessSandboxAdapter()
    order = adapter.submit_order(market="BTC/SAR", side="buy", price="250000", quantity="0.001", idempotency_key="k1")
    assert adapter.get_order(order.order_id) == order
    assert adapter.cancel_order(order.order_id).status == "cancelled"


def test_local_sandbox_idempotency_and_validation():
    adapter = InProcessSandboxAdapter()
    args = dict(market="BTC/SAR", side="buy", price="10", quantity="1", idempotency_key="same")
    assert adapter.submit_order(**args).order_id == adapter.submit_order(**args).order_id
    with pytest.raises(ValueError, match="different order"):
        adapter.submit_order(**{**args, "market": "ETH/SAR"})
    with pytest.raises(ValueError):
        adapter.submit_order(**{**args, "price": "NaN", "idempotency_key": "invalid"})


def test_testnet_requires_credentials(monkeypatch):
    monkeypatch.delenv("BINANCE_TESTNET_API_KEY", raising=False)
    monkeypatch.delenv("BINANCE_TESTNET_API_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="credentials are required"):
        build_execution_adapter("binance_testnet")


def test_testnet_mode_is_explicit_and_still_testnet(monkeypatch):
    monkeypatch.setenv("BINANCE_TESTNET_API_KEY", "test-key")
    monkeypatch.setenv("BINANCE_TESTNET_API_SECRET", "test-secret")
    adapter = build_execution_adapter("binance_testnet")
    assert isinstance(adapter, BinanceSpotTestnetAdapter)
    assert adapter.mode == "external_testnet_only"
    assert TESTNET_BASE_URL == "https://testnet.binance.vision"


def test_testnet_rejects_sar_pairs_before_network():
    adapter = BinanceSpotTestnetAdapter("key", "secret")
    with pytest.raises(ValueError, match="USDT pairs"):
        adapter.submit_order(market="BTC/SAR", side="buy", price="1", quantity="1", idempotency_key="order-1")


def test_testnet_submit_get_cancel_use_fixed_testnet_endpoint(monkeypatch):
    adapter = BinanceSpotTestnetAdapter("test-key", "test-secret")
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        method = request.get_method()
        if method == "POST":
            return FakeResponse({
                "symbol": "BTCUSDT", "orderId": 123, "clientOrderId": "order-1",
                "side": "BUY", "price": "65000", "origQty": "0.001",
                "status": "NEW", "transactTime": 1760000000000,
            })
        if method == "GET":
            return FakeResponse({
                "symbol": "BTCUSDT", "orderId": 123, "side": "BUY",
                "price": "65000", "origQty": "0.001", "status": "NEW",
                "time": 1760000000000,
            })
        return FakeResponse({
            "symbol": "BTCUSDT", "orderId": 123, "side": "BUY",
            "price": "65000", "origQty": "0.001", "status": "CANCELED",
            "time": 1760000000000,
        })

    monkeypatch.setattr("app.binance_testnet.urllib.request.urlopen", fake_urlopen)
    order = adapter.submit_order(
        market="BTC/USDT", side="buy", price="65000", quantity="0.001",
        idempotency_key="order-1",
    )
    assert order.order_id == "123"
    assert order.status == "open"
    assert adapter.get_order("123").status == "open"
    assert adapter.cancel_order("123").status == "cancelled"
    assert len(calls) == 3
    for request, timeout in calls:
        assert request.full_url.startswith(TESTNET_BASE_URL + "/api/v3/order")
        assert "api.binance.com" not in request.full_url
        assert timeout == 8.0
    post_body = parse_qs(calls[0][0].data.decode())
    assert post_body["symbol"] == ["BTCUSDT"]
    assert post_body["newClientOrderId"] == ["order-1"]
    assert "signature" in post_body


def test_testnet_adapter_rejects_invalid_amount_and_idempotency():
    adapter = BinanceSpotTestnetAdapter("key", "secret")
    with pytest.raises(ValueError):
        adapter.submit_order(market="BTC/USDT", side="buy", price="Infinity", quantity="1", idempotency_key="order-1")
    with pytest.raises(ValueError):
        adapter.submit_order(market="BTC/USDT", side="buy", price="1", quantity="1", idempotency_key="bad key")

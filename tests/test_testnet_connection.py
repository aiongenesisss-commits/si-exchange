import json

from app.binance_testnet import BinanceSpotTestnetAdapter


class FakeResponse:
    def __init__(self, data):
        self.payload = json.dumps(data).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_check_connection_uses_signed_read_only_account_endpoint(monkeypatch):
    adapter = BinanceSpotTestnetAdapter("test-key", "test-secret")
    calls = []

    def fake_urlopen(request, timeout):
        calls.append((request, timeout))
        assert request.get_method() == "GET"
        assert request.full_url.startswith("https://testnet.binance.vision/api/v3/account?")
        assert "api.binance.com" not in request.full_url
        assert request.get_header("X-mbx-apikey") == "test-key"
        return FakeResponse({"balances": [{"asset": "USDT", "free": "1000", "locked": "0"}]})

    monkeypatch.setattr("app.binance_testnet.urllib.request.urlopen", fake_urlopen)
    result = adapter.check_connection()
    assert result == {
        "connected": True,
        "can_read_account": True,
        "nonzero_asset_count": 1,
        "mode": "external_testnet_only",
    }
    assert len(calls) == 1
    assert calls[0][1] == 8.0


def test_check_connection_rejects_unexpected_response(monkeypatch):
    adapter = BinanceSpotTestnetAdapter("test-key", "test-secret")

    def fake_urlopen(request, timeout):
        return FakeResponse({"unexpected": True})

    monkeypatch.setattr("app.binance_testnet.urllib.request.urlopen", fake_urlopen)
    import pytest
    with pytest.raises(RuntimeError, match="Unexpected account response"):
        adapter.check_connection()

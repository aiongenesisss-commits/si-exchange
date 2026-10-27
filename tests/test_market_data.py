import json

from app import market_data


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


def reset_cache():
    market_data._cache = None
    market_data._cache_at = 0.0


def test_live_prices_are_converted_to_indicative_sar(monkeypatch):
    reset_cache()
    payload = [
        {"symbol": pair, "price": "100.0"}
        for pair in market_data.ASSET_SYMBOLS.values()
    ]
    monkeypatch.setattr(market_data, "urlopen", lambda *_args, **_kwargs: FakeResponse(payload))

    result = market_data.get_live_prices_sar()

    assert result["BTC/SAR"]["price_sar"] == 375.0
    assert result["BTC/SAR"]["is_live"] is True
    assert "indicative" in result["BTC/SAR"]["price_source"]
    assert result["USDT/SAR"]["is_live"] is False
    assert result["USDT/SAR"]["price_sar"] == 3.75


def test_unavailable_public_feed_returns_none(monkeypatch):
    reset_cache()

    def fail(*_args, **_kwargs):
        raise OSError("offline")

    monkeypatch.setattr(market_data, "urlopen", fail)
    assert market_data.get_live_prices_sar() is None

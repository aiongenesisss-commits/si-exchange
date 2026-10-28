from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app import main


def test_market_data_status_marks_fresh_stale_and_aion_unverified(monkeypatch):
    now = datetime.now(timezone.utc)
    monkeypatch.setattr(
        main,
        "get_live_prices_sar",
        lambda: {
            "BTC/SAR": {
                "price_sar": 250000.0,
                "is_live": True,
                "price_source": "public ticker; indicative SAR conversion",
                "updated_at": now.isoformat(),
            },
            "ETH/SAR": {
                "price_sar": 9000.0,
                "is_live": True,
                "price_source": "public ticker; indicative SAR conversion",
                "updated_at": (now - timedelta(minutes=3)).isoformat(),
            },
        },
    )

    with TestClient(main.app) as client:
        response = client.get("/market-data-status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "read_only_market_data_status"
    assert payload["real_orders_enabled"] is False
    assert payload["money_movement_enabled"] is False
    markets = {item["symbol"]: item for item in payload["markets"]}
    assert markets["BTC/SAR"]["status"] == "live_reference_fresh"
    assert markets["BTC/SAR"]["executable_sar_quote"] is False
    assert markets["ETH/SAR"]["status"] == "stale"
    assert markets["ETH/SAR"]["is_live"] is False
    assert markets["AION/SAR"]["status"] == "simulated_unverified"
    assert markets["AION/SAR"]["is_live"] is False


def test_market_data_status_fails_closed_when_feed_unavailable(monkeypatch):
    monkeypatch.setattr(main, "get_live_prices_sar", lambda: None)

    with TestClient(main.app) as client:
        response = client.get("/market-data-status")

    assert response.status_code == 200
    payload = response.json()
    markets = {item["symbol"]: item for item in payload["markets"]}
    assert markets["BTC/SAR"]["status"] == "unavailable_or_fallback"
    assert markets["BTC/SAR"]["is_live"] is False
    assert markets["AION/SAR"]["status"] == "simulated_unverified"
    assert all(item["executable_sar_quote"] is False for item in markets.values())


def test_dashboard_exposes_market_data_status_panel():
    with TestClient(main.app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert 'id="marketDataStatus"' in response.text
    assert "refreshMarketStatus()" in response.text


def test_market_data_status_marks_invalid_timestamp_unavailable(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_live_prices_sar",
        lambda: {
            "BTC/SAR": {
                "price_sar": 250000.0,
                "is_live": True,
                "price_source": "test reference source",
                "updated_at": "not-a-timestamp",
            }
        },
    )

    with TestClient(main.app) as client:
        response = client.get("/market-data-status")

    assert response.status_code == 200
    payload = response.json()
    markets = {item["symbol"]: item for item in payload["markets"]}
    assert markets["BTC/SAR"]["status"] == "invalid_timestamp"
    assert markets["BTC/SAR"]["is_live"] is False
    assert markets["BTC/SAR"]["executable_sar_quote"] is False


def test_dashboard_renders_source_and_timestamp_fields():
    with TestClient(main.app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "x.source" in response.text
    assert "x.updated_at" in response.text
    assert "x.age_seconds" in response.text

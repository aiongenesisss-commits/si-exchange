from fastapi.testclient import TestClient

from app.main import app, balances, idempotency_keys, ledger, orders

client = TestClient(app)


def reset_demo_state():
    orders.clear()
    ledger.clear()
    idempotency_keys.clear()
    for account in balances:
        balances[account]["SAR"] = 100000.0
        balances[account].update({
            "BTC": 0.25, "ETH": 2.0, "BNB": 10.0, "SOL": 20.0,
            "XRP": 500.0, "ADA": 500.0, "DOGE": 1000.0, "TRX": 5000.0,
            "LTC": 2.0, "DOT": 20.0, "LINK": 20.0, "AION": 100000.0, "USDT": 1000.0, "USDC": 1000.0,
        })


def test_market_catalog_has_14_simulated_crypto_pairs():
    reset_demo_state()
    response = client.get("/markets")
    assert response.status_code == 200
    markets = response.json()
    assert len(markets) == 14
    assert {item["symbol"] for item in markets} == {
        "BTC/SAR", "ETH/SAR", "BNB/SAR", "SOL/SAR", "XRP/SAR",
        "ADA/SAR", "DOGE/SAR", "TRX/SAR", "LTC/SAR", "DOT/SAR",
        "LINK/SAR", "AION/SAR", "USDT/SAR", "USDC/SAR",
    }
    assert all(item["simulated_price_sar"] > 0 for item in markets)


def test_non_btc_eth_market_uses_correct_base_asset_and_audits():
    reset_demo_state()
    sell = client.post(
        "/orders",
        json={"market": "SOL/SAR", "side": "sell", "account": "A", "price": 600, "quantity": 1},
    )
    buy = client.post(
        "/orders",
        json={"market": "SOL/SAR", "side": "buy", "account": "B", "price": 600, "quantity": 1},
    )
    assert sell.status_code == 201
    assert buy.status_code == 201
    assert buy.json()["status"] == "filled"
    current = client.get("/balances").json()["balances"]
    assert current["A"]["SOL"] == 19.0
    assert current["B"]["SOL"] == 21.0
    audit = client.get("/audit").json()
    assert audit["valid"] is True
    assert audit["issues"] == []

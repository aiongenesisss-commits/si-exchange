from fastapi.testclient import TestClient
from app.main import app, orders, ledger, balances, INITIAL_ASSETS

client = TestClient(app)

def setup_function():
    orders.clear()
    ledger.clear()
    balances.clear()
    balances.update({
        "A": {"SAR": 100000.0, **INITIAL_ASSETS.copy()},
        "B": {"SAR": 100000.0, **INITIAL_ASSETS.copy()},
    })

def test_dashboard_is_arabic_rtl_and_api_is_simulation_only():
    page = client.get("/")
    assert page.status_code == 200
    assert 'lang="ar"' in page.text and 'dir="rtl"' in page.text
    body = client.get("/api").json()
    assert body["mode"] == "simulation_only"
    assert body["live_trading"] is False
    assert body["deposits_enabled"] is False
    assert body["withdrawals_enabled"] is False

def test_markets_and_demo_balances():
    markets = client.get("/markets").json()
    assert {m["symbol"] for m in markets} == {"BTC/SAR", "ETH/SAR", "BNB/SAR", "SOL/SAR", "XRP/SAR", "ADA/SAR", "DOGE/SAR", "TRX/SAR", "LTC/SAR", "DOT/SAR", "LINK/SAR", "AION/SAR", "USDT/SAR", "USDC/SAR"}
    response = client.get("/balances").json()
    assert response["mode"] == "demo_only"
    assert response["balances"]["A"]["SAR"] == 100000
    assert response["balances"]["B"]["BTC"] == 0.25

def test_limit_orders_match_record_ledger_and_update_both_accounts():
    sell = client.post("/orders", json={"market":"BTC/SAR","side":"sell","account":"A","price":250000,"quantity":0.01})
    assert sell.status_code == 201 and sell.json()["status"] == "open"
    buy = client.post("/orders", json={"market":"BTC/SAR","side":"buy","account":"B","price":250000,"quantity":0.01})
    assert buy.status_code == 201 and buy.json()["status"] == "filled"
    assert client.get(f"/orders/{sell.json()['id']}").json()["status"] == "filled"
    fill = client.get("/ledger").json()[0]
    assert fill["simulated_value_sar"] == 2500
    updated = client.get("/balances").json()["balances"]
    assert updated["A"]["BTC"] == 0.24
    assert updated["A"]["SAR"] == 102500
    assert updated["B"]["BTC"] == 0.26
    assert updated["B"]["SAR"] == 97500

def test_buy_matches_resting_sell_below_buy_limit_at_resting_price():
    sell = client.post("/orders", json={"market":"BTC/SAR","side":"sell","account":"A","price":249000,"quantity":0.01})
    buy = client.post("/orders", json={"market":"BTC/SAR","side":"buy","account":"B","price":250000,"quantity":0.01})
    assert sell.status_code == 201 and buy.status_code == 201
    assert buy.json()["status"] == "filled"
    fill = client.get("/ledger").json()[0]
    assert fill["price"] == 249000
    assert fill["simulated_value_sar"] == 2490

def test_sell_matches_resting_buy_above_sell_limit_at_resting_price():
    buy = client.post("/orders", json={"market":"BTC/SAR","side":"buy","account":"A","price":250000,"quantity":0.01})
    sell = client.post("/orders", json={"market":"BTC/SAR","side":"sell","account":"B","price":249000,"quantity":0.01})
    assert buy.status_code == 201 and sell.status_code == 201
    assert sell.json()["status"] == "filled"
    assert client.get(f"/orders/{buy.json()['id']}").json()["status"] == "filled"
    fill = client.get("/ledger").json()[0]
    assert fill["price"] == 250000
    balances_now = client.get("/balances").json()["balances"]
    assert balances_now["A"]["SAR"] == 97500
    assert balances_now["B"]["SAR"] == 102500

def test_non_crossing_orders_remain_open_without_ledger_or_balance_changes():
    sell = client.post("/orders", json={"market":"BTC/SAR","side":"sell","account":"A","price":251000,"quantity":0.01})
    buy = client.post("/orders", json={"market":"BTC/SAR","side":"buy","account":"B","price":250000,"quantity":0.01})
    assert sell.json()["status"] == "open"
    assert buy.json()["status"] == "open"
    assert client.get("/ledger").json() == []
    assert client.get("/balances").json()["balances"]["A"]["BTC"] == 0.25
    assert client.get("/balances").json()["balances"]["B"]["SAR"] == 100000

def test_same_demo_account_orders_do_not_match_each_other():
    sell = client.post("/orders", json={"market":"BTC/SAR","side":"sell","account":"A","price":250000,"quantity":0.01})
    buy = client.post("/orders", json={"market":"BTC/SAR","side":"buy","account":"A","price":250000,"quantity":0.01})
    assert sell.json()["status"] == "open"
    assert buy.json()["status"] == "open"
    assert client.get("/ledger").json() == []

def test_rejects_non_positive_price_and_quantity():
    assert client.post("/orders", json={"market":"ETH/SAR","side":"buy","price":0,"quantity":1}).status_code == 422
    assert client.post("/orders", json={"market":"ETH/SAR","side":"buy","price":9000,"quantity":-1}).status_code == 422

def test_missing_order_returns_404():
    assert client.get("/orders/not-real").status_code == 404


def test_aion_sar_is_simulation_only_and_trades_only_demo_balances():
    markets = {item["symbol"]: item for item in client.get("/markets").json()}
    aion_market = markets["AION/SAR"]
    assert aion_market["is_live"] is False
    assert aion_market["simulated_price_sar"] == 0.10
    assert "Fallback simulated price" in aion_market["price_source"]
    assert client.get("/api").json()["live_trading"] is False

    sell = client.post("/orders", json={"market":"AION/SAR","side":"sell","account":"A","price":0.10,"quantity":10})
    buy = client.post("/orders", json={"market":"AION/SAR","side":"buy","account":"B","price":0.10,"quantity":10})
    assert sell.status_code == 201 and buy.status_code == 201
    assert buy.json()["status"] == "filled"
    fill = client.get("/ledger").json()[0]
    assert fill["market"] == "AION/SAR"
    assert fill["simulated_value_sar"] == 1.0
    after = client.get("/balances").json()["balances"]
    assert after["A"]["AION"] == 99990
    assert after["B"]["AION"] == 100010
    assert client.get("/audit").json()["valid"] is True

from fastapi.testclient import TestClient
from app.main import app, orders, ledger

client = TestClient(app)

def setup_function():
    orders.clear()
    ledger.clear()

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
    assert {m["symbol"] for m in markets} == {"BTC/SAR", "ETH/SAR"}
    assert client.get("/balances").json()["mode"] == "demo_only"

def test_limit_orders_match_and_record_ledger():
    sell = client.post("/orders", json={"market":"BTC/SAR","side":"sell","price":250000,"quantity":0.01})
    assert sell.status_code == 201 and sell.json()["status"] == "open"
    buy = client.post("/orders", json={"market":"BTC/SAR","side":"buy","price":250000,"quantity":0.01})
    assert buy.status_code == 201 and buy.json()["status"] == "filled"
    assert client.get("/ledger").json()[0]["simulated_value_sar"] == 2500
    assert client.get(f"/orders/{sell.json()['id']}").json()["status"] == "filled"

def test_rejects_non_positive_price_and_quantity():
    assert client.post("/orders", json={"market":"ETH/SAR","side":"buy","price":0,"quantity":1}).status_code == 422
    assert client.post("/orders", json={"market":"ETH/SAR","side":"buy","price":9000,"quantity":-1}).status_code == 422

def test_missing_order_returns_404():
    assert client.get("/orders/not-real").status_code == 404

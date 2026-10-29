"""Arabic RTL simulation-only SI Exchange demo."""
from datetime import datetime, timezone
import os
import json
import math
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import List
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from app.market_data import get_live_prices_sar
from app import postgres_store, redis_store

app = FastAPI(title="SI Exchange Demo API", description="Simulation only; no real-money services.", version="0.1.0")

# Production guard: this app has no verified identity provider/account isolation yet.
# Lock private demo-account APIs on managed hosting until authentication is implemented.
from fastapi import Request
from fastapi.responses import JSONResponse

_PRIVATE_API_PATHS = {"/balances", "/available-balances", "/orders", "/ledger", "/audit"}


def _is_managed_deployment() -> bool:
    return any(os.getenv(name) for name in ("VERCEL", "RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID"))


@app.middleware("http")
async def lock_private_demo_apis_until_auth(request: Request, call_next):
    path = request.url.path
    is_private = path in _PRIVATE_API_PATHS or path.startswith("/orders/")
    if is_private and (_is_managed_deployment() or os.getenv("AION_ACCESS_MODE", "").strip().lower() == "locked"):
        return JSONResponse(
            status_code=503,
            content={
                "detail": "Private demo APIs are locked until verified authentication and account isolation are configured.",
                "code": "private_api_locked",
                "simulation_only": True,
            },
        )
    return await call_next(request)



def _postgres_enabled() -> bool:
    return os.getenv("AION_STORAGE_BACKEND", "memory").strip().lower() == "postgres"


def _redis_enabled() -> bool:
    return os.getenv("AION_STORAGE_BACKEND", "memory").strip().lower() == "redis"


def _persist_redis_state():
    redis_store.save_state({
        "balances": balances,
        "orders": [item.model_dump(mode="json") for item in orders],
        "ledger": [item.model_dump(mode="json") for item in ledger],
        "idempotency_keys": {key: {"fingerprint": value[0], "order_id": value[1]} for key, value in idempotency_keys.items()},
    })


@app.on_event("startup")
def configure_storage():
    if _postgres_enabled():
        # Fail closed: never silently switch to volatile memory if PostgreSQL is requested.
        postgres_store.check_connection()
        postgres_store.initialize_demo_accounts()
    elif _redis_enabled():
        # Redis is already provisioned with a persistent Railway volume. Never fall back silently.
        redis_store.check_connection()
        state = redis_store.load_state()
        if state:
            balances.clear()
            balances.update(state["balances"])
            orders[:] = [Order.model_validate(item) for item in state.get("orders", [])]
            ledger[:] = [Fill.model_validate(item) for item in state.get("ledger", [])]
            idempotency_keys.clear()
            idempotency_keys.update({
                key: (item["fingerprint"], item["order_id"])
                for key, item in state.get("idempotency_keys", {}).items()
            })

class Market(str, Enum):
    BTC_SAR = "BTC/SAR"
    ETH_SAR = "ETH/SAR"
    BNB_SAR = "BNB/SAR"
    SOL_SAR = "SOL/SAR"
    XRP_SAR = "XRP/SAR"
    ADA_SAR = "ADA/SAR"
    DOGE_SAR = "DOGE/SAR"
    TRX_SAR = "TRX/SAR"
    LTC_SAR = "LTC/SAR"
    DOT_SAR = "DOT/SAR"
    LINK_SAR = "LINK/SAR"
    AION_SAR = "AION/SAR"
    USDT_SAR = "USDT/SAR"
    USDC_SAR = "USDC/SAR"
class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"
class Account(str, Enum):
    A = "A"
    B = "B"
class OrderRequest(BaseModel):
    market: Market
    side: Side
    account: Account = Account.A
    price: float = Field(gt=0, le=1_000_000_000)
    quantity: float = Field(gt=0, le=1_000_000)
class Order(BaseModel):
    id: str
    market: Market
    side: Side
    account: Account
    price: float
    quantity: float
    remaining_quantity: float
    status: str
    created_at: datetime
class Fill(BaseModel):
    id: str
    order_id: str
    maker_order_id: str
    taker_order_id: str
    buyer_account: Account
    seller_account: Account
    market: Market
    side: Side
    price: float
    quantity: float
    simulated_value_sar: float
    created_at: datetime

lock = Lock()
orders: List[Order] = []
ledger: List[Fill] = []
prices = {
    Market.BTC_SAR: 250000.0,
    Market.ETH_SAR: 9000.0,
    Market.BNB_SAR: 2500.0,
    Market.SOL_SAR: 600.0,
    Market.XRP_SAR: 9.0,
    Market.ADA_SAR: 1.5,
    Market.DOGE_SAR: 0.7,
    Market.TRX_SAR: 1.1,
    Market.LTC_SAR: 300.0,
    Market.DOT_SAR: 25.0,
    Market.LINK_SAR: 60.0,
    # Clearly simulated seed only; not a live market quote or claim of deployed token/liquidity.
    Market.AION_SAR: 0.10,
    Market.USDT_SAR: 3.75,
    Market.USDC_SAR: 3.75,
}
INITIAL_ASSETS = {
    "BTC": 0.25, "ETH": 2.0, "BNB": 10.0, "SOL": 20.0,
    "XRP": 500.0, "ADA": 500.0, "DOGE": 1000.0, "TRX": 5000.0,
    "LTC": 2.0, "DOT": 20.0, "LINK": 20.0, "AION": 100000.0, "USDT": 1000.0, "USDC": 1000.0,
}
balances = {
    account: {"SAR": 100000.0, **INITIAL_ASSETS.copy()}
    for account in ("A", "B")
}
idempotency_keys = {}  # process-local demo cache; not durable across restarts/instances
INITIAL_TOTALS = {"SAR": 200000.0, **{asset: quantity * 2 for asset, quantity in INITIAL_ASSETS.items()}}

PAGE = """<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SI Exchange</title>
<style>body{margin:0;background:#0b1220;color:#edf4ff;font:16px Tahoma,Arial}header,main{max-width:1000px;margin:auto;padding:20px}header{border-bottom:1px solid #263750}h1{margin:0}p{line-height:1.7;color:#a9bad0}.warning{padding:12px;background:#382d12;border-right:4px solid #fbbf24;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{background:#121d30;border:1px solid #263750;border-radius:12px;padding:16px;margin:12px 0}.price{font-size:24px;color:#5eead4}label{display:block;margin:10px 0 5px;color:#a9bad0}input,select,button{width:100%;padding:10px;border-radius:8px;border:1px solid #354760;background:#0b1525;color:white;box-sizing:border-box}button{margin-top:12px;background:#5eead4;color:#062b2b;font-weight:bold}table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:right;padding:9px;border-bottom:1px solid #263750}.scroll{overflow:auto}.balance{display:inline-block;background:#0b1525;padding:10px;border-radius:8px;margin:4px}</style>
<header><h1>SI Exchange</h1><p>لوحة تداول تجريبية بواجهة عربية RTL</p><strong style="color:#5eead4">محاكاة فقط — لا أموال حقيقية</strong></header><main><p class="warning">تنبيه: قد تُعرض أسعار مرجعية مباشرة من Binance مع تحويل SAR تقريبي؛ وقد تظهر أسعار احتياطية تجريبية عند تعذر المصدر. جميع الأرصدة والأوامر والتنفيذ تجريبية ومؤقتة. لا توجد إيداعات أو سحوبات أو حفظ أصول أو تداول حي.</p>
<section class="card"><h3>حالة شبكات AION</h3><p id="networkStatus">جاري قراءة سجل الشبكات...</p></section><section class="card"><h3>الأسواق التجريبية مقابل الريال السعودي</h3><div id="marketCards" class="grid">تحميل الأسواق…</div></section><section class="card"><h3>الأرصدة التجريبية</h3><div id="balances">تحميل…</div></section>
<div class="grid"><section class="card"><h3>إنشاء أمر محدد السعر</h3><form id="f"><label>السوق</label><select id="market"></select><label>المتداول التجريبي</label><select id="account"><option value="A">المتداول A</option><option value="B">المتداول B</option></select><label>النوع</label><select id="side"><option value="buy">شراء</option><option value="sell">بيع</option></select><label>السعر بالريال</label><input id="price" type="number" min="0.000001" step="any" value="250000" required><label>الكمية</label><input id="qty" type="number" min="0.000001" step="any" value="0.001" required><p>السعر المقترح يتغير حسب السوق. الأمر المحدد لا يُنفّذ إلا عند وجود أمر معاكس بسعر متوافق.</p><button>إرسال أمر تجريبي</button><p id="msg" role="status"></p></form></section><section class="card"><h3>ضوابط السلامة</h3><p>مطابقة أوامر محددة السعر وتسجيل التنفيذ في دفتر تجريبي. لا اتصال بمحافظ أو شبكات بلوك تشين أو مزودي دفع. ليست منصة مالية إنتاجية.</p></section></div>
<section class="card"><h3>الأوامر</h3><div class="scroll"><table><thead><tr><th>السوق</th><th>النوع</th><th>السعر</th><th>الكمية</th><th>المتبقي</th><th>الحالة</th></tr></thead><tbody id="orders"></tbody></table></div></section>
<section class="card"><h3>دفتر التنفيذ التجريبي</h3><div class="scroll"><table><thead><tr><th>السوق</th><th>النوع</th><th>السعر</th><th>الكمية</th><th>القيمة SAR</th></tr></thead><tbody id="ledger"></tbody></table></div></section></main>
<script>const $=id=>document.getElementById(id),fmt=n=>Number(n).toLocaleString('ar-SA',{maximumFractionDigits:8});async function get(p){let r=await fetch(p);if(!r.ok)throw Error('تعذر الاتصال');return r.json()}let marketData=[];async function refreshNetworks(){try{let n=await get('/networks');$('networkStatus').textContent=n.networks.map(x=>x.name+' (Chain ID '+x.chain_id+'): '+(x.status==='planned'?'مخططة، غير منشورة':x.status)).join(' | ')+' — العقود المجانية: '+(n.free_deployments.status==='not_enabled'?'غير مفعّلة حالياً':'الحالة بحاجة إلى مراجعة')}catch(e){$('networkStatus').textContent='تعذر تحميل حالة الشبكات؛ لا تفترض أنها منشورة'}}function updatePriceDefaults(){const m=marketData.find(x=>x.symbol===$('market').value);if(m){$('price').value=m.simulated_price_sar;$('qty').value=m.symbol.startsWith('BTC/')?'0.001':m.symbol.startsWith('ETH/')?'0.01':m.symbol.startsWith('USDT/')||m.symbol.startsWith('USDC/')?'10':'1'}}async function refresh(){try{let m=await get('/markets'),b=await get('/balances'),o=await get('/orders'),l=await get('/ledger');marketData=m;$('marketCards').innerHTML=m.map(x=>'<section class="card"><h3>'+x.symbol+'</h3><div class="price">'+fmt(x.simulated_price_sar)+' ر.س</div><small>'+(x.is_live?('سعر سوق مباشر — '+x.price_source):x.price_source)+'</small></section>').join('');const selected=$('market').value;$('market').innerHTML=m.map(x=>'<option value="'+x.symbol+'">'+x.symbol+'</option>').join('');if(m.some(x=>x.symbol===selected))$('market').value=selected;updatePriceDefaults();$('balances').innerHTML=Object.entries(b.balances).map(([a,items])=>'<div><b>المتداول '+a+'</b>'+Object.entries(items).map(([k,v])=>'<span class="balance">'+k+': <b>'+fmt(v)+'</b></span>').join('')+'</div>').join('');$('orders').innerHTML=o.slice().reverse().map(x=>'<tr><td>'+x.market+'</td><td>'+(x.side==='buy'?'شراء':'بيع')+'</td><td>'+fmt(x.price)+'</td><td>'+fmt(x.quantity)+'</td><td>'+fmt(x.remaining_quantity)+'</td><td>'+x.status+'</td></tr>').join('')||'<tr><td colspan="6">لا توجد أوامر</td></tr>';$('ledger').innerHTML=l.slice().reverse().map(x=>'<tr><td>'+x.market+'</td><td>'+(x.side==='buy'?'شراء':'بيع')+'</td><td>'+fmt(x.price)+'</td><td>'+fmt(x.quantity)+'</td><td>'+fmt(x.simulated_value_sar)+'</td></tr>').join('')||'<tr><td colspan="5">لا توجد عمليات تنفيذ</td></tr>'}catch(e){$('msg').textContent=e.message}}$('market').addEventListener('change',updatePriceDefaults);$('f').addEventListener('submit',async e=>{e.preventDefault();try{let r=await fetch('/orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({market:$('market').value,side:$('side').value,account:$('account').value,price:Number($('price').value),quantity:Number($('qty').value)})}),d=await r.json();if(!r.ok)throw Error(JSON.stringify(d.detail));$('msg').textContent='تم إنشاء الأمر التجريبي: '+d.status;await refresh()}catch(e){$('msg').textContent='خطأ: '+e.message}});refresh();refreshNetworks();</script></html>"""

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(PAGE)

@app.get("/api")
def api_root():
    return {"name":"SI Exchange","mode":"simulation_only","live_trading":False,"deposits_enabled":False,"withdrawals_enabled":False,"custody_enabled":False}

@app.get("/health")
def health():
    if _postgres_enabled():
        try:
            postgres_store.check_connection()
            return {"status":"ok","mode":"simulation_only","storage":"postgres"}
        except Exception:
            raise HTTPException(status_code=503, detail="Configured PostgreSQL storage unavailable")
    if _redis_enabled():
        try:
            redis_store.check_connection()
            return {"status":"ok","mode":"simulation_only","storage":"redis"}
        except Exception:
            raise HTTPException(status_code=503, detail="Configured Redis storage unavailable")
    return {"status":"ok","mode":"simulation_only","storage":"memory_demo"}

@app.get("/ready")
def readiness():
    """Deployment readiness probe; never reports planned chains or vaults as live."""
    if _postgres_enabled():
        try:
            postgres_store.check_connection()
            return {
                "status": "ready",
                "mode": "simulation_only",
                "storage": "postgres",
                "durable_demo_storage": True,
                "real_money_enabled": False,
                "blockchain_connected": False,
                "digital_vault_live": False,
            }
        except Exception:
            raise HTTPException(status_code=503, detail="Configured PostgreSQL storage unavailable")
    if _redis_enabled():
        try:
            redis_store.check_connection()
            return {
                "status": "ready",
                "mode": "simulation_only",
                "storage": "redis",
                "durable_demo_storage": True,
                "real_money_enabled": False,
                "blockchain_connected": False,
                "digital_vault_live": False,
            }
        except Exception:
            raise HTTPException(status_code=503, detail="Configured Redis storage unavailable")
    return {
        "status": "ready",
        "mode": "simulation_only",
        "storage": "memory_demo",
        "durable_demo_storage": False,
        "real_money_enabled": False,
        "blockchain_connected": False,
        "digital_vault_live": False,
    }

@app.get("/networks")
def get_network_registry():
    """Read-only registry of AION network readiness; never returns secret values."""
    registry_path = Path(__file__).resolve().parents[1] / "networks" / "aion_networks.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise HTTPException(status_code=503, detail="AION network registry unavailable or invalid")

    # Return only allow-listed public status fields.
    networks = []
    for item in registry.get("networks", []):
        networks.append({
            "key": item.get("key"),
            "name": item.get("name"),
            "chain_id": item.get("chain_id"),
            "status": item.get("status"),
            "purpose": item.get("purpose"),
            "native_currency": item.get("native_currency"),
            "public_rpc_url": item.get("public_rpc_url"),
            "explorer_url": item.get("explorer_url"),
            "token_deployed": item.get("token_deployed"),
            "token_contract_address": item.get("token_contract_address"),
            "public_network_verified": False if item.get("status") == "planned" else None,
        })

    return {
        "status": registry.get("status", "configuration_only"),
        "warning": registry.get("warning", "Do not assume planned networks are public or live."),
        "networks": networks,
        "free_deployments": registry.get("free_deployments", {"status": "not_enabled"}),
        "mode": "read_only_registry",
        "real_money_enabled": False,
    }

@app.get("/online-manifest")
def online_manifest():
    """Public, non-secret inventory of what is and is not actually online."""
    return {
        "platform": "SI Exchange",
        "deployment_mode": "simulation_only",
        "dashboard": "online_when_this_service_is_reachable",
        "api_health": "/health",
        "readiness": "/ready",
        "markets": "/markets",
        "balances": "/balances",
        "orders": "/orders",
        "ledger": "/ledger",
        "integrity_audit": "/audit",
        "network_registry": "/networks",
        "components": {
            "demo_exchange": "available",
            "persistent_storage": "configured_only_when_AION_STORAGE_BACKEND_is_postgres_or_redis",
            "aion_nova_chain_id_71101": "planned_not_live",
            "aion_orbit_chain_id_71102": "planned_not_live",
            "aion_coin_on_chain": "not_verified_deployed",
            "digital_vault": "not_implemented_for_real_assets",
            "real_deposits_withdrawals_custody": "disabled",
            "live_trading": "disabled",
        },
        "security_note": "Never send private keys, seed phrases, API secrets, or signing credentials to this public API.",
    }

@app.get("/production-readiness")
def production_readiness():
    """Report production blockers without exposing secrets or implying readiness."""
    managed = any(os.getenv(name) for name in ("VERCEL", "RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID"))
    postgres_configured = (
        os.getenv("AION_STORAGE_BACKEND", "memory").strip().lower() == "postgres"
        and bool(os.getenv("DATABASE_URL"))
    )
    blockers = ["verified_authentication_not_implemented", "per_user_account_isolation_not_implemented"]
    if not postgres_configured:
        blockers.append("persistent_postgresql_not_configured")
    return {
        "status": "not_production_ready",
        "mode": "simulation_only",
        "checks": {
            "verified_authentication": False,
            "per_user_account_isolation": False,
            "persistent_database_configured": postgres_configured,
            "managed_deployment_detected": managed,
            "real_deposits_withdrawals_custody": False,
            "live_trading": False,
        },
        "blockers": blockers,
        "note": "Configuration presence is not a successful connection test. This endpoint never enables financial capabilities.",
    }


# Authenticated per-user scoping for local/staging environments.
# Managed deployments remain locked by lock_private_demo_apis_until_auth until separately reviewed.
@app.middleware("http")
async def enforce_demo_account_scope(request: Request, call_next):
    from starlette.responses import JSONResponse, Response
    from app.auth import AuthenticationError, account_for_subject, verify_access_token

    path = request.url.path
    private = path in _PRIVATE_API_PATHS or path.startswith("/orders/")
    if not private:
        return await call_next(request)
    if _is_managed_deployment():
        return JSONResponse(status_code=503, content={
            "detail": "Private demo APIs remain locked on managed hosting pending security review.",
            "code": "private_api_locked", "simulation_only": True,
        })
    if os.getenv("AION_AUTH_REQUIRED", "").strip().lower() != "true":
        return await call_next(request)

    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer ") or not authorization[7:].strip():
        return JSONResponse(status_code=401, content={"detail": "Bearer token required"})
    try:
        claims = verify_access_token(authorization[7:].strip())
        account = account_for_subject(claims["sub"])
    except (AuthenticationError, KeyError):
        return JSONResponse(status_code=401, content={"detail": "Invalid or unauthorized bearer token"})

    # Make idempotency keys unique per verified account, not across tenants.
    if request.headers.get("Idempotency-Key"):
        headers = list(request.scope.get("headers", []))
        headers = [(k, v) for k, v in headers if k.lower() != b"idempotency-key"]
        scoped_key = f"{account}:{request.headers['Idempotency-Key']}".encode()
        headers.append((b"idempotency-key", scoped_key))
        request.scope["headers"] = headers

    # Never trust the account field in a request body; overwrite it with server-side mapping.
    if request.method == "POST" and path == "/orders":
        try:
            body = await request.body()
            payload = json.loads(body or b"{}")
            payload["account"] = account
            body = json.dumps(payload).encode()
            sent = False
            async def receive():
                nonlocal sent
                if not sent:
                    sent = True
                    return {"type": "http.request", "body": body, "more_body": False}
                return {"type": "http.request", "body": b"", "more_body": False}
            request = Request(request.scope, receive=receive)
        except (ValueError, TypeError):
            return JSONResponse(status_code=400, content={"detail": "Invalid order request body"})

    request.state.demo_account = account
    response = await call_next(request)
    if response.status_code >= 400:
        return response
    if path == "/orders/" or path.startswith("/orders/"):
        # Order detail must never disclose another account's order.
        try:
            chunks = [chunk async for chunk in response.body_iterator]
            data = json.loads(b"".join(chunks))
            if data.get("account") != account:
                return JSONResponse(status_code=404, content={"detail": "Order not found"})
            return JSONResponse(status_code=response.status_code, content=data)
        except Exception:
            return JSONResponse(status_code=500, content={"detail": "Unable to scope order response"})
    if path in {"/balances", "/available-balances", "/orders", "/ledger", "/audit"}:
        try:
            chunks = [chunk async for chunk in response.body_iterator]
            data = json.loads(b"".join(chunks))
            if path == "/balances":
                data["balances"] = {account: data.get("balances", {}).get(account, {})}
            elif path == "/available-balances":
                data["available_balances"] = {account: data.get("available_balances", {}).get(account, {})}
            elif path == "/orders":
                data = [item for item in data if item.get("account") == account]
            elif path == "/ledger":
                data = [item for item in data if account in (item.get("buyer_account"), item.get("seller_account"))]
            elif path == "/audit":
                # Global audit issue details can contain other users' data; expose only status/counts.
                data = {"mode": data.get("mode", "simulation_only"), "valid": data.get("valid", False),
                        "orders_checked": None, "fills_checked": None, "issues": []}
            return JSONResponse(status_code=response.status_code, content=data)
        except Exception:
            return JSONResponse(status_code=500, content={"detail": "Unable to scope private response"})
    return response


@app.get("/markets")
def get_markets():
    live = get_live_prices_sar()
    result = []
    for market, fallback_price in prices.items():
        # AION is not a verified on-chain token; never accept a live quote for it.
        record = None if market == Market.AION_SAR else (live or {}).get(market.value)
        if record:
            result.append({
                "symbol": market.value,
                "simulated_price_sar": record["price_sar"],
                "is_live": record["is_live"],
                "price_source": record["price_source"],
                "updated_at": record["updated_at"],
                "trading_mode": "simulation_only",
            })
        else:
            result.append({
                "symbol": market.value,
                "simulated_price_sar": fallback_price,
                "is_live": False,
                "price_source": (
                    "AION AUTONOMOUS project token — simulated only; no verified deployment or live quote"
                    if market == Market.AION_SAR
                    else "Fallback simulated price; live market data unavailable"
                ),
                "updated_at": None,
                "trading_mode": "simulation_only",
            })
    return result

@app.get("/balances")
def get_balances():
    if _postgres_enabled():
        try: return postgres_store.balances()
        except Exception: raise HTTPException(status_code=503, detail="PostgreSQL storage unavailable")
    with lock:
        return {"mode":"demo_only","balances":{account: assets.copy() for account, assets in balances.items()}}

def _reserved_amount(account: Account, asset: str) -> float:
    """Return funds reserved by active demo orders for one account and asset."""
    reserved = 0.0
    for resting in orders:
        if resting.account != account or resting.status not in ("open", "partially_filled"):
            continue
        base_asset = resting.market.value.split("/")[0]
        if asset == "SAR" and resting.side == Side.BUY:
            reserved += resting.price * resting.remaining_quantity
        elif asset == base_asset and resting.side == Side.SELL:
            reserved += resting.remaining_quantity
    return reserved


@app.get("/available-balances")
def get_available_balances():
    if _postgres_enabled():
        try: return postgres_store.available_balances()
        except Exception: raise HTTPException(status_code=503, detail="PostgreSQL storage unavailable")
    with lock:
        available = {}
        for account, assets in balances.items():
            available[account] = {
                asset: round(max(0.0, value - _reserved_amount(Account(account), asset)), 8)
                for asset, value in assets.items()
            }
        return {"mode": "demo_only", "available_balances": available}


@app.get("/orders", response_model=List[Order])
def get_orders():
    if _postgres_enabled():
        try: return postgres_store.list_orders()
        except Exception: raise HTTPException(status_code=503, detail="PostgreSQL storage unavailable")
    with lock:
        return list(orders)

@app.post("/orders", response_model=Order, status_code=201)
def place_order(request: OrderRequest, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")):
    if _postgres_enabled():
        try:
            result = postgres_store.place_order(request, idempotency_key)
            if result.get("error") == "idempotency_conflict":
                raise HTTPException(status_code=409, detail="Idempotency-Key already used with a different request")
            if result.get("error") == "insufficient_funds":
                raise HTTPException(status_code=409, detail=f"Insufficient available demo {result.get('asset')} after open-order reservations")
            return result
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=503, detail="PostgreSQL order transaction failed")
    now = datetime.now(timezone.utc)
    fingerprint = json.dumps(request.model_dump(mode="json"), sort_keys=True)
    order = Order(id=str(uuid4()),market=request.market,side=request.side,account=request.account,price=request.price,quantity=request.quantity,remaining_quantity=request.quantity,status="open",created_at=now)
    with lock:
        if idempotency_key:
            if len(idempotency_key) > 200:
                raise HTTPException(status_code=400, detail="Idempotency-Key must be 200 characters or fewer")
            prior = idempotency_keys.get(idempotency_key)
            if prior:
                if prior[0] != fingerprint:
                    raise HTTPException(status_code=409, detail="Idempotency-Key already used with a different request")
                for prior_order in orders:
                    if prior_order.id == prior[1]:
                        return prior_order
                raise HTTPException(status_code=409, detail="Idempotency-Key record is inconsistent")
        base_asset = order.market.value.split("/")[0]
        if order.side == Side.BUY:
            required = order.price * order.quantity
            available = balances[order.account]["SAR"] - _reserved_amount(order.account, "SAR")
            if available + 1e-8 < required:
                raise HTTPException(status_code=409, detail="Insufficient available demo SAR after open-order reservations")
        else:
            available = balances[order.account][base_asset] - _reserved_amount(order.account, base_asset)
            if available + 1e-12 < order.quantity:
                raise HTTPException(status_code=409, detail=f"Insufficient available demo {base_asset} after open-order reservations")
        # Snapshot mutable demo state before matching so a failed Redis write can roll back.
        redis_persistence_enabled = _redis_enabled()
        balances_snapshot = {account: assets.copy() for account, assets in balances.items()} if redis_persistence_enabled else None
        orders_snapshot = [Order.model_validate(item.model_dump()) for item in orders] if redis_persistence_enabled else None
        ledger_snapshot = [Fill.model_validate(item.model_dump()) for item in ledger] if redis_persistence_enabled else None
        idempotency_snapshot = idempotency_keys.copy() if redis_persistence_enabled else None

        matches=[o for o in orders if o.market==order.market and o.side!=order.side and o.account!=order.account and o.status in ("open","partially_filled") and (o.price<=order.price if order.side==Side.BUY else o.price>=order.price)]
        matches.sort(key=lambda o:(o.price if order.side==Side.BUY else -o.price,o.created_at))
        for resting in matches:
            if order.remaining_quantity<=0: break
            qty=min(order.remaining_quantity,resting.remaining_quantity)
            base_asset = order.market.value.split("/")[0]
            value = round(resting.price * qty, 8)
            buyer = order.account if order.side == Side.BUY else resting.account
            seller = resting.account if order.side == Side.BUY else order.account
            if balances[buyer]["SAR"] + 1e-8 < value or balances[seller][base_asset] + 1e-12 < qty:
                continue
            balances[buyer]["SAR"] = round(balances[buyer]["SAR"] - value, 8)
            balances[buyer][base_asset] = round(balances[buyer][base_asset] + qty, 12)
            balances[seller][base_asset] = round(balances[seller][base_asset] - qty, 12)
            balances[seller]["SAR"] = round(balances[seller]["SAR"] + value, 8)
            ledger.append(Fill(id=str(uuid4()),order_id=order.id,maker_order_id=resting.id,taker_order_id=order.id,buyer_account=buyer,seller_account=seller,market=order.market,side=order.side,price=resting.price,quantity=qty,simulated_value_sar=value,created_at=now))
            resting.remaining_quantity=round(resting.remaining_quantity-qty,12)
            resting.status="filled" if resting.remaining_quantity==0 else "partially_filled"
            order.remaining_quantity=round(order.remaining_quantity-qty,12)
        order.status="filled" if order.remaining_quantity==0 else ("partially_filled" if order.remaining_quantity<order.quantity else "open")
        orders.append(order)
        if idempotency_key:
            idempotency_keys[idempotency_key] = (fingerprint, order.id)
        if redis_persistence_enabled:
            try:
                _persist_redis_state()
            except Exception:
                # Restore all in-memory mutations: a failed persistence must not leave an
                # order/fill/balance change that a retry could accidentally execute again.
                balances.clear()
                balances.update(balances_snapshot)
                orders[:] = orders_snapshot
                ledger[:] = ledger_snapshot
                idempotency_keys.clear()
                idempotency_keys.update(idempotency_snapshot)
                raise HTTPException(status_code=503, detail="Redis persistence failed; no order was committed")
    return order

@app.get("/audit")
def integrity_audit():
    """Check demo order/fill linkage, balance conservation, and nonnegative balances."""
    if _postgres_enabled():
        try: return postgres_store.audit()
        except Exception: raise HTTPException(status_code=503, detail="PostgreSQL audit unavailable")
    issues = []
    with lock:
        known_order_ids = {o.id for o in orders}
        filled_by_order = {o.id: 0.0 for o in orders}
        for fill in ledger:
            if fill.maker_order_id not in known_order_ids or fill.taker_order_id not in known_order_ids:
                issues.append(f"fill {fill.id}: references unknown order")
            if fill.maker_order_id == fill.taker_order_id:
                issues.append(f"fill {fill.id}: maker and taker are identical")
            if fill.buyer_account == fill.seller_account:
                issues.append(f"fill {fill.id}: self-trade detected")
            filled_by_order[fill.maker_order_id] = filled_by_order.get(fill.maker_order_id, 0.0) + fill.quantity
            filled_by_order[fill.taker_order_id] = filled_by_order.get(fill.taker_order_id, 0.0) + fill.quantity
            if not math.isfinite(fill.quantity) or fill.quantity <= 0 or not math.isfinite(fill.simulated_value_sar):
                issues.append(f"fill {fill.id}: invalid numeric values")
        for order in orders:
            if abs((filled_by_order.get(order.id, 0.0) + order.remaining_quantity) - order.quantity) > 1e-8:
                issues.append(f"order {order.id}: quantity does not reconcile with fills and remainder")
        for account, assets in balances.items():
            for asset, value in assets.items():
                if not math.isfinite(value) or value < -1e-8:
                    issues.append(f"account {account} asset {asset}: invalid balance")
        for asset, expected in INITIAL_TOTALS.items():
            actual = sum(account_balances[asset] for account_balances in balances.values())
            if abs(actual - expected) > 1e-6:
                issues.append(f"asset {asset}: balance conservation mismatch")
        return {"mode": "simulation_only", "valid": not issues, "orders_checked": len(orders), "fills_checked": len(ledger), "issues": issues}

@app.get("/ledger", response_model=List[Fill])
def get_ledger():
    if _postgres_enabled():
        try: return postgres_store.list_fills()
        except Exception: raise HTTPException(status_code=503, detail="PostgreSQL storage unavailable")
    with lock:
        return list(ledger)

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    if _postgres_enabled():
        try:
            order = postgres_store.get_order(order_id)
            if order: return order
            raise HTTPException(status_code=404, detail="Order not found")
        except HTTPException: raise
        except Exception: raise HTTPException(status_code=503, detail="PostgreSQL storage unavailable")
    with lock:
        for order in orders:
            if order.id==order_id: return order
    raise HTTPException(status_code=404,detail="Order not found")

"""Arabic RTL simulation-only SI Exchange demo."""
from datetime import datetime, timezone
from enum import Enum
from threading import Lock
from typing import List
from uuid import uuid4
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="SI Exchange Demo API", description="Simulation only; no real-money services.", version="0.1.0")

class Market(str, Enum):
    BTC_SAR = "BTC/SAR"
    ETH_SAR = "ETH/SAR"
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
    market: Market
    side: Side
    price: float
    quantity: float
    simulated_value_sar: float
    created_at: datetime

lock = Lock()
orders: List[Order] = []
ledger: List[Fill] = []
prices = {Market.BTC_SAR: 250000.0, Market.ETH_SAR: 9000.0}
balances = {account: {"SAR": 100000.0, "BTC": 0.25, "ETH": 2.0} for account in ("A", "B")}

PAGE = """<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SI Exchange</title>
<style>body{margin:0;background:#0b1220;color:#edf4ff;font:16px Tahoma,Arial}header,main{max-width:1000px;margin:auto;padding:20px}header{border-bottom:1px solid #263750}h1{margin:0}p{line-height:1.7;color:#a9bad0}.warning{padding:12px;background:#382d12;border-right:4px solid #fbbf24;border-radius:8px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px}.card{background:#121d30;border:1px solid #263750;border-radius:12px;padding:16px;margin:12px 0}.price{font-size:24px;color:#5eead4}label{display:block;margin:10px 0 5px;color:#a9bad0}input,select,button{width:100%;padding:10px;border-radius:8px;border:1px solid #354760;background:#0b1525;color:white;box-sizing:border-box}button{margin-top:12px;background:#5eead4;color:#062b2b;font-weight:bold}table{width:100%;border-collapse:collapse;font-size:13px}td,th{text-align:right;padding:9px;border-bottom:1px solid #263750}.scroll{overflow:auto}.balance{display:inline-block;background:#0b1525;padding:10px;border-radius:8px;margin:4px}</style>
<header><h1>SI Exchange</h1><p>لوحة تداول تجريبية بواجهة عربية RTL</p><strong style="color:#5eead4">محاكاة فقط — لا أموال حقيقية</strong></header><main><p class="warning">تنبيه: جميع الأسعار والأرصدة والأوامر افتراضية. لا توجد إيداعات أو سحوبات أو حفظ أصول أو تداول حي، وتُمسح البيانات عند إعادة تشغيل التطبيق.</p>
<div class="grid"><section class="card"><h3>BTC / SAR</h3><div class="price" id="btc">—</div></section><section class="card"><h3>ETH / SAR</h3><div class="price" id="eth">—</div></section><section class="card"><h3>الأرصدة التجريبية</h3><div id="balances">تحميل…</div></section></div>
<div class="grid"><section class="card"><h3>إنشاء أمر محدد السعر</h3><form id="f"><label>السوق</label><select id="market"><option>BTC/SAR</option><option>ETH/SAR</option></select><label>المتداول التجريبي</label><select id="account"><option value="A">المتداول A</option><option value="B">المتداول B</option></select><label>النوع</label><select id="side"><option value="buy">شراء</option><option value="sell">بيع</option></select><label>السعر بالريال</label><input id="price" type="number" min="0.000001" step="any" value="250000" required><label>الكمية</label><input id="qty" type="number" min="0.000001" step="any" value="0.001" required><p>السعر المقترح يتغير حسب السوق. الأمر المحدد لا يُنفّذ إلا عند وجود أمر معاكس بسعر متوافق.</p><button>إرسال أمر تجريبي</button><p id="msg" role="status"></p></form></section><section class="card"><h3>ضوابط السلامة</h3><p>مطابقة أوامر محددة السعر وتسجيل التنفيذ في دفتر تجريبي. لا اتصال بمحافظ أو شبكات بلوك تشين أو مزودي دفع. ليست منصة مالية إنتاجية.</p></section></div>
<section class="card"><h3>الأوامر</h3><div class="scroll"><table><thead><tr><th>السوق</th><th>النوع</th><th>السعر</th><th>الكمية</th><th>المتبقي</th><th>الحالة</th></tr></thead><tbody id="orders"></tbody></table></div></section>
<section class="card"><h3>دفتر التنفيذ التجريبي</h3><div class="scroll"><table><thead><tr><th>السوق</th><th>النوع</th><th>السعر</th><th>الكمية</th><th>القيمة SAR</th></tr></thead><tbody id="ledger"></tbody></table></div></section></main>
<script>const $=id=>document.getElementById(id),fmt=n=>Number(n).toLocaleString('ar-SA',{maximumFractionDigits:8});async function get(p){let r=await fetch(p);if(!r.ok)throw Error('تعذر الاتصال');return r.json()}async function refresh(){try{let m=await get('/markets'),b=await get('/balances'),o=await get('/orders'),l=await get('/ledger');$('btc').textContent=fmt(m[0].simulated_price_sar)+' ر.س';$('eth').textContent=fmt(m[1].simulated_price_sar)+' ر.س';$('balances').innerHTML=Object.entries(b.balances).map(([a,items])=>'<div><b>المتداول '+a+'</b>'+Object.entries(items).map(([k,v])=>'<span class="balance">'+k+': <b>'+fmt(v)+'</b></span>').join('')+'</div>').join('');$('orders').innerHTML=o.slice().reverse().map(x=>'<tr><td>'+x.market+'</td><td>'+(x.side==='buy'?'شراء':'بيع')+'</td><td>'+fmt(x.price)+'</td><td>'+fmt(x.quantity)+'</td><td>'+fmt(x.remaining_quantity)+'</td><td>'+x.status+'</td></tr>').join('')||'<tr><td colspan="6">لا توجد أوامر</td></tr>';$('ledger').innerHTML=l.slice().reverse().map(x=>'<tr><td>'+x.market+'</td><td>'+(x.side==='buy'?'شراء':'بيع')+'</td><td>'+fmt(x.price)+'</td><td>'+fmt(x.quantity)+'</td><td>'+fmt(x.simulated_value_sar)+'</td></tr>').join('')||'<tr><td colspan="5">لا توجد عمليات تنفيذ</td></tr>'}catch(e){$('msg').textContent=e.message}}$('market').addEventListener('change',()=>{$('price').value=$('market').value==='BTC/SAR'?'250000':'9000';$('qty').value=$('market').value==='BTC/SAR'?'0.001':'0.01'});$('f').addEventListener('submit',async e=>{e.preventDefault();try{let r=await fetch('/orders',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({market:$('market').value,side:$('side').value,account:$('account').value,price:Number($('price').value),quantity:Number($('qty').value)})}),d=await r.json();if(!r.ok)throw Error(JSON.stringify(d.detail));$('msg').textContent='تم إنشاء الأمر التجريبي: '+d.status;await refresh()}catch(e){$('msg').textContent='خطأ: '+e.message}});refresh();</script></html>"""

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(PAGE)

@app.get("/api")
def api_root():
    return {"name":"SI Exchange","mode":"simulation_only","live_trading":False,"deposits_enabled":False,"withdrawals_enabled":False,"custody_enabled":False}

@app.get("/health")
def health():
    return {"status":"ok","mode":"simulation_only"}

@app.get("/markets")
def get_markets():
    return [{"symbol":m.value,"simulated_price_sar":p} for m,p in prices.items()]

@app.get("/balances")
def get_balances():
    with lock:
        return {"mode":"demo_only","balances":{account: assets.copy() for account, assets in balances.items()}}

@app.get("/orders", response_model=List[Order])
def get_orders():
    with lock:
        return list(orders)

@app.post("/orders", response_model=Order, status_code=201)
def place_order(request: OrderRequest):
    now = datetime.now(timezone.utc)
    order = Order(id=str(uuid4()),market=request.market,side=request.side,account=request.account,price=request.price,quantity=request.quantity,remaining_quantity=request.quantity,status="open",created_at=now)
    with lock:
        matches=[o for o in orders if o.market==order.market and o.side!=order.side and o.account!=order.account and o.status in ("open","partially_filled") and (o.price<=order.price if order.side==Side.BUY else o.price>=order.price)]
        matches.sort(key=lambda o:(o.price if order.side==Side.BUY else -o.price,o.created_at))
        for resting in matches:
            if order.remaining_quantity<=0: break
            qty=min(order.remaining_quantity,resting.remaining_quantity)
            base_asset = "BTC" if order.market == Market.BTC_SAR else "ETH"
            value = round(resting.price * qty, 8)
            buyer = order.account if order.side == Side.BUY else resting.account
            seller = resting.account if order.side == Side.BUY else order.account
            if balances[buyer]["SAR"] + 1e-8 < value or balances[seller][base_asset] + 1e-12 < qty:
                continue
            balances[buyer]["SAR"] = round(balances[buyer]["SAR"] - value, 8)
            balances[buyer][base_asset] = round(balances[buyer][base_asset] + qty, 12)
            balances[seller][base_asset] = round(balances[seller][base_asset] - qty, 12)
            balances[seller]["SAR"] = round(balances[seller]["SAR"] + value, 8)
            ledger.append(Fill(id=str(uuid4()),order_id=order.id,market=order.market,side=order.side,price=resting.price,quantity=qty,simulated_value_sar=value,created_at=now))
            resting.remaining_quantity=round(resting.remaining_quantity-qty,12)
            resting.status="filled" if resting.remaining_quantity==0 else "partially_filled"
            order.remaining_quantity=round(order.remaining_quantity-qty,12)
        order.status="filled" if order.remaining_quantity==0 else ("partially_filled" if order.remaining_quantity<order.quantity else "open")
        orders.append(order)
    return order

@app.get("/ledger", response_model=List[Fill])
def get_ledger():
    with lock:
        return list(ledger)

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    with lock:
        for order in orders:
            if order.id==order_id: return order
    raise HTTPException(status_code=404,detail="Order not found")

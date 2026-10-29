"""Standalone browser-only SI Exchange demonstration.

No network requests, server-side state, storage, credentials, wallets, or real funds.
Refreshing the page resets the simulation.
"""

DEMO_PAGE = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SI Exchange — محاكاة مستقلة</title>
<style>
:root{color-scheme:dark;--bg:#07111f;--panel:#102039;--line:#2a405c;--text:#eef5ff;--muted:#a9bbd0;--accent:#76e0c3;--gold:#f3cf76;--red:#ff9b9b}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#122d4b,#07111f 60%);color:var(--text);font:15px system-ui,Tahoma,Arial;line-height:1.6}
.wrap{width:min(1120px,94%);margin:auto;padding:22px 0 42px}header{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap;padding-bottom:16px;border-bottom:1px solid var(--line)}
.brand{font-size:13px;font-weight:900;letter-spacing:.08em;color:var(--accent)}h1{margin:8px 0 2px;font-size:clamp(24px,4vw,36px)}h2{font-size:17px;margin:0 0 12px}p{margin:6px 0;color:var(--muted)}
.pill{display:inline-block;border:1px solid #7c6737;color:var(--gold);background:#2c2517;border-radius:999px;padding:4px 10px;font-size:12px}
.warning{margin:18px 0;padding:14px;border:1px solid #8a7136;border-right:5px solid var(--gold);border-radius:12px;background:#241f15}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:14px 0}
.panel{min-width:0;background:linear-gradient(145deg,#132741,#0c192b);border:1px solid var(--line);border-radius:15px;padding:16px}
.big{font-size:25px;font-weight:850;color:var(--accent);font-variant-numeric:tabular-nums}.muted{color:var(--muted);font-size:12px}
.controls{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px;align-items:end}
label{display:block;color:var(--muted);font-size:12px;margin-bottom:5px}
input,select,button{font:inherit;border-radius:9px;padding:10px;border:1px solid var(--line);background:#07111f;color:var(--text);width:100%}
button{background:#173b50;cursor:pointer;font-weight:800}button:hover{filter:brightness(1.12)}button.primary{background:var(--accent);color:#06201e;border-color:transparent}
.two{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:right;padding:8px 6px;border-bottom:1px solid #263a51;vertical-align:top}th{color:var(--muted);font-weight:650}
.scroll{overflow:auto}.positive{color:var(--accent)}.negative{color:var(--red)}.empty{color:var(--muted);padding:10px 0}.footer{margin-top:18px;border-top:1px solid var(--line);padding-top:12px;color:var(--muted);font-size:12px}
@media(max-width:760px){.grid{grid-template-columns:1fr}.two{grid-template-columns:1fr}.controls{grid-template-columns:1fr 1fr}.controls .wide{grid-column:1/-1}}
</style>
</head>
<body>
<main class="wrap">
<header>
  <div><div class="brand">AION AUTONOMOUS GLOBAL NETWORK</div><h1>SI Exchange</h1><p>لوحة تداول تجريبية مستقلة لعرض آلية الأوامر والمطابقة والسجل.</p></div>
  <span class="pill">محاكاة فقط · لا أموال حقيقية</span>
</header>
<section class="warning">
  <strong>تنبيه مهم:</strong>
  <span>كل الأسعار والأرصدة والأوامر هنا بيانات افتراضية داخل المتصفح فقط. سعر AION/SAR هو قيمة تجريبية ثابتة قدرها 0.10 ريال، وليس سعر سوق أو إثباتًا لنشر العملة. لا توجد اتصالات بخادم أو بلوكتشين أو محافظ أو بوابات دفع. تحديث الصفحة يمسح المحاكاة.</span>
</section>
<section class="grid" aria-label="الأسواق">
  <div class="panel"><div class="muted">السوق المحدد</div><div id="marketName" class="big">AION/SAR</div><div class="muted">سعر مرجعي تجريبي</div></div>
  <div class="panel"><div class="muted">السعر الافتراضي</div><div id="marketPrice" class="big">0.10 ر.س</div><div class="muted">ليس سعر تداول حقيقيًا</div></div>
  <div class="panel"><div class="muted">حالة المحاكاة</div><div id="auditState" class="big">سليمة مبدئيًا</div><div class="muted">يمكن فحص حفظ مجموع الأرصدة</div></div>
</section>
<section class="panel">
  <h2>إرسال أمر محدد السعر</h2>
  <form id="orderForm" class="controls">
    <div><label for="market">السوق</label><select id="market"><option>AION/SAR</option><option>BTC/SAR</option><option>ETH/SAR</option></select></div>
    <div><label for="account">الحساب التجريبي</label><select id="account"><option value="A">الحساب A</option><option value="B">الحساب B</option></select></div>
    <div><label for="side">نوع الأمر</label><select id="side"><option value="buy">شراء</option><option value="sell">بيع</option></select></div>
    <div><label for="price">السعر (ريال)</label><input id="price" type="number" min="0.00000001" step="any" value="0.10" required></div>
    <div><label for="quantity">الكمية</label><input id="quantity" type="number" min="0.00000001" step="any" value="10" required></div>
    <div class="wide"><button class="primary" type="submit">إرسال الأمر التجريبي</button></div>
    <div class="wide muted">المطابقة تتم فقط بين الحسابين التجريبيين A وB داخل هذه الصفحة، دون أي اتصال خارجي.</div>
  </form>
  <p id="message" role="status" aria-live="polite"></p>
</section>
<section class="two">
  <div class="panel"><h2>الأرصدة الافتراضية</h2><div class="scroll"><table><thead><tr><th>الحساب</th><th>AION</th><th>BTC</th><th>ETH</th><th>SAR</th></tr></thead><tbody id="balances"></tbody></table></div></div>
  <div class="panel"><h2>الأوامر والسوق المحدد</h2><div class="scroll"><table><thead><tr><th>المعرّف</th><th>الحساب</th><th>النوع</th><th>السعر</th><th>المتبقي</th><th>الحالة</th></tr></thead><tbody id="orders"></tbody></table></div><div id="ordersEmpty" class="empty">لا توجد أوامر بعد.</div></div>
</section>
<section class="panel" style="margin-top:12px">
  <div style="display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap"><h2>سجل التنفيذات المحاكية</h2><button id="auditButton" type="button" style="width:auto">فحص سلامة الأرصدة</button></div>
  <div class="scroll"><table><thead><tr><th>المعرّف</th><th>السوق</th><th>المشتري</th><th>البائع</th><th>السعر</th><th>الكمية</th><th>القيمة (ر.س)</th></tr></thead><tbody id="ledger"></tbody></table></div><div id="ledgerEmpty" class="empty">لم تُنفّذ أي مطابقة بعد.</div>
</section>
<div class="footer">نسخة عرض متصفح مستقلة — لا تحفظ البيانات بعد إعادة التحميل، ولا تمثل منصة تداول أو خدمة مالية مرخصة. لا تُدخل بيانات شخصية أو مفاتيح محافظ.</div>
</main>
<script>
(function(){
"use strict";
var prices={"AION/SAR":0.10,"BTC/SAR":250000,"ETH/SAR":9000};
var initialAssets={AION:100000,BTC:1,ETH:10};
var initialCash=100000;
var state, sequence;
function reset(){state={balances:{A:{SAR:initialCash,AION:initialAssets.AION,BTC:initialAssets.BTC,ETH:initialAssets.ETH},B:{SAR:initialCash,AION:initialAssets.AION,BTC:initialAssets.BTC,ETH:initialAssets.ETH}},orders:[],fills:[]};sequence=1;}
function num(n){return Number(n).toLocaleString("en-US",{maximumFractionDigits:8});}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});}
function base(m){return m.split("/")[0];}
function available(account,asset){var reserved=0;state.orders.forEach(function(o){if(o.account!==account||o.remaining<=0)return;if(o.side==="buy"&&asset==="SAR")reserved+=o.remaining*o.price;if(o.side==="sell"&&asset===base(o.market))reserved+=o.remaining;});return state.balances[account][asset]-reserved;}
function render(){
 var market=document.getElementById("market").value;
 document.getElementById("marketName").textContent=market;
 document.getElementById("marketPrice").textContent=num(prices[market])+" ر.س";
 document.getElementById("balances").innerHTML=["A","B"].map(function(a){return "<tr><td>الحساب "+a+"</td><td>"+num(state.balances[a].AION)+"</td><td>"+num(state.balances[a].BTC)+"</td><td>"+num(state.balances[a].ETH)+"</td><td>"+num(state.balances[a].SAR)+"</td></tr>";}).join("");
 var selected=state.orders.filter(function(o){return o.market===market;}).slice().reverse();
 document.getElementById("orders").innerHTML=selected.map(function(o){return "<tr><td>"+esc(o.id)+"</td><td>"+o.account+"</td><td>"+(o.side==="buy"?"شراء":"بيع")+"</td><td>"+num(o.price)+"</td><td>"+num(o.remaining)+"</td><td>"+(o.status==="filled"?"مكتمل":o.status==="partial"?"جزئي":"مفتوح")+"</td></tr>";}).join("");
 document.getElementById("ordersEmpty").style.display=selected.length?"none":"block";
 var fills=state.fills.filter(function(f){return f.market===market;}).slice().reverse();
 document.getElementById("ledger").innerHTML=fills.map(function(f){return "<tr><td>"+esc(f.id)+"</td><td>"+esc(f.market)+"</td><td>"+f.buyer+"</td><td>"+f.seller+"</td><td>"+num(f.price)+"</td><td>"+num(f.quantity)+"</td><td>"+num(f.value)+"</td></tr>";}).join("");
 document.getElementById("ledgerEmpty").style.display=fills.length?"none":"block";
}
function place(event){
 event.preventDefault();
 var market=document.getElementById("market").value, account=document.getElementById("account").value;
 var side=document.getElementById("side").value, price=Number(document.getElementById("price").value), quantity=Number(document.getElementById("quantity").value);
 var message=document.getElementById("message"), asset=base(market);
 if(!Number.isFinite(price)||!Number.isFinite(quantity)||price<=0||quantity<=0){message.textContent="أدخل سعرًا وكمية أكبر من صفر.";message.className="negative";return;}
 var required=side==="buy"?price*quantity:quantity, assetToCheck=side==="buy"?"SAR":asset;
 if(available(account,assetToCheck)+1e-8<required){message.textContent="الرصيد المتاح في الحساب التجريبي غير كافٍ لهذا الأمر.";message.className="negative";return;}
 var incoming={id:"O"+String(sequence++).padStart(4,"0"),market:market,account:account,side:side,price:price,quantity:quantity,remaining:quantity,status:"open",created:Date.now()};
 var matches=state.orders.filter(function(o){return o.market===market&&o.side!==side&&o.account!==account&&o.remaining>0&&(side==="buy"?o.price<=price:o.price>=price);});
 matches.sort(function(a,b){if(side==="buy"&&a.price!==b.price)return a.price-b.price;if(side==="sell"&&a.price!==b.price)return b.price-a.price;return a.created-b.created;});
 matches.forEach(function(resting){
  if(incoming.remaining<=1e-10)return;
  var qty=Math.min(incoming.remaining,resting.remaining), executionPrice=resting.price, value=qty*executionPrice;
  var buyer=side==="buy"?account:resting.account, seller=side==="sell"?account:resting.account;
  if(state.balances[buyer].SAR+1e-8<value||state.balances[seller][asset]+1e-8<qty)return;
  state.balances[buyer].SAR-=value;state.balances[buyer][asset]+=qty;
  state.balances[seller][asset]-=qty;state.balances[seller].SAR+=value;
  incoming.remaining-=qty;resting.remaining-=qty;
  resting.status=resting.remaining<=1e-8?"filled":"partial";
  state.fills.push({id:"F"+String(sequence++).padStart(4,"0"),market:market,buyer:buyer,seller:seller,price:executionPrice,quantity:qty,value:value});
 });
 incoming.remaining=Math.max(0,incoming.remaining);
 incoming.status=incoming.remaining<=1e-8?"filled":incoming.remaining<incoming.quantity?"partial":"open";
 state.orders.push(incoming);
 message.textContent=incoming.status==="filled"?"تمت مطابقة الأمر بالكامل داخل المحاكاة.":incoming.status==="partial"?"تمت مطابقة جزء من الأمر، والباقي مفتوح.":"تم تسجيل الأمر في دفتر الأوامر التجريبي.";
 message.className="positive";render();
}
document.getElementById("market").addEventListener("change",function(){document.getElementById("price").value=prices[this.value];render();});
document.getElementById("orderForm").addEventListener("submit",place);
document.getElementById("auditButton").addEventListener("click",function(){
 var assets=["SAR","AION","BTC","ETH"],valid=true;
 assets.forEach(function(a){var expected=a==="SAR"?initialCash*2:initialAssets[a]*2;var actual=state.balances.A[a]+state.balances.B[a];if(Math.abs(actual-expected)>1e-6)valid=false;});
 document.getElementById("auditState").textContent=valid?"سليمة":"تحتاج مراجعة";
 document.getElementById("auditState").className=valid?"big positive":"big negative";
 document.getElementById("message").textContent=valid?"اجتاز مجموع الأرصدة الافتراضية فحص الحفظ.":"فشل فحص مجموع الأرصدة الافتراضية.";
 document.getElementById("message").className=valid?"positive":"negative";
});
reset();document.getElementById("price").value=prices[document.getElementById("market").value];render();
})();
</script>
</body>
</html>
"""

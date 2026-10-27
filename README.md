# SI Exchange — Arabic simulated exchange demo

A runnable FastAPI demonstration with an Arabic right-to-left (RTL) dashboard, 13 simulated crypto/SAR markets (BTC, ETH, BNB, SOL, XRP, ADA, DOGE, TRX, LTC, DOT, LINK, USDT, USDC), demo balances, limit orders, basic price-time matching, and an execution ledger.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `/` for the Arabic dashboard, `/docs` for API docs, `/markets` for the 13 simulated prices, `/balances` for demo balances, `/orders` for orders, `/ledger` for simulated fills, and `/audit` for a read-only integrity check.

## Tests

```bash
pytest
```

## Integrity and retry behavior

- Fill records identify both maker and taker orders and their simulated buyer/seller accounts.
- `GET /audit` checks order quantity reconciliation, fill references, self-trade invariants, nonnegative finite balances, and conservation of demo asset totals.
- `POST /orders` accepts an optional `Idempotency-Key` header. Replaying the same key and payload returns the original order; reusing a key with a different payload returns HTTP 409.
- The idempotency cache is process-local and volatile. It is not a durable guarantee across restarts or multiple serverless instances; this is intentionally a demo-only safeguard, not production settlement protection.

## Safety boundary

Simulation only. There are no real deposits, withdrawals, custody, payment processing, wallet keys, blockchain connections, or live trading. Demo data is in memory and resets when the process restarts. This is a prototype, not production financial software.

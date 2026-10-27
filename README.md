# SI Exchange — Arabic simulated exchange demo

A runnable FastAPI demonstration with an Arabic right-to-left (RTL) dashboard, 13 simulated crypto/SAR markets (BTC, ETH, BNB, SOL, XRP, ADA, DOGE, TRX, LTC, DOT, LINK, USDT, USDC), demo balances, limit orders, basic price-time matching, and an execution ledger.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `/` for the Arabic dashboard, `/docs` for API docs, `/networks` for the read-only AION Nova/Orbit status registry, `/online-manifest` for an online component inventory, `/markets` for simulated market state/reference prices, `/balances` for demo balances, `/orders` for orders, `/ledger` for simulated fills, and `/audit` for a read-only integrity check. `/networks` intentionally reports both chains as planned and the free-deployment promotion as disabled until public infrastructure is actually verified.

## Tests

```bash
pytest
```

## Integrity and retry behavior

- Fill records identify both maker and taker orders and their simulated buyer/seller accounts.
- `GET /audit` checks order quantity reconciliation, fill references, self-trade invariants, nonnegative finite balances, and conservation of demo asset totals.
- `POST /orders` accepts an optional `Idempotency-Key` header. Replaying the same key and payload returns the original order; reusing a key with a different payload returns HTTP 409.
- In the default memory backend, idempotency keys are process-local and volatile. The opt-in PostgreSQL backend stores idempotency keys durably and serializes matching transactions, but it remains demo-only and is not production settlement protection.

## Optional durable PostgreSQL backend

The default remains in-memory for a simple demo. To persist demo balances, orders, fills, idempotency keys, and audit events across process restarts, configure PostgreSQL explicitly:

1. Set `DATABASE_URL` as a deployment secret.
2. Apply the schema with `DATABASE_URL="$DATABASE_URL" bash scripts/apply_migrations.sh`.
3. Set `AION_STORAGE_BACKEND=postgres` and restart the app.
4. Confirm `/health` reports `storage: postgres`, then check `/audit`.

See [PostgreSQL operations](docs/POSTGRES-PERSISTENCE-OPERATIONS.md). If PostgreSQL mode is requested but the database is missing/unavailable, startup fails rather than silently reverting to volatile memory. CI exercises the PostgreSQL path against a temporary database.

## AION offline OS prototype

A bootable Debian Live ISO build and QEMU health smoke test are defined in [the OS build workflow](.github/workflows/aion-os-image.yml). The image is intended to bundle Python wheels so its dashboard can run without public internet access after boot. The build still relies on external Debian/Python repositories; full reproducibility, disconnected updates/rollback, secure boot, and physical-hardware validation remain open gates.

## Safety boundary

Simulation only. There are no real deposits, withdrawals, custody, payment processing, wallet keys, blockchain connections, or live trading. In-memory demo data resets on process restart; PostgreSQL mode is opt-in and stores only demo data. This is a prototype, not production financial software.

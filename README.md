# SI Exchange — Arabic simulated exchange demo

A runnable FastAPI demonstration with an Arabic right-to-left (RTL) dashboard, simulated BTC/SAR and ETH/SAR markets, demo balances, limit orders, basic price-time matching, and an execution ledger.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open `/` for the Arabic dashboard, `/docs` for API docs, `/markets` for simulated prices, `/balances` for demo balances, `/orders` for orders, and `/ledger` for simulated fills.

## Tests

```bash
pytest
```

## Safety boundary

Simulation only. There are no real deposits, withdrawals, custody, payment processing, wallet keys, blockchain connections, or live trading. Demo data is in memory and resets when the process restarts. This is a prototype, not production financial software.

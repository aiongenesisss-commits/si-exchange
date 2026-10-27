# Next implementation step

The PostgreSQL schema has been merged. The API still uses in-memory state. Before claiming durable persistence, wire all order, balance, fill, and idempotency operations into atomic PostgreSQL transactions and test concurrency, rollback, and restart behavior. Keep the application simulation-only; no deposits, withdrawals, custody, wallet keys, blockchain calls, or live trading.

# Running PostgreSQL schema migrations

This repository contains a PostgreSQL schema for **simulated** SI Exchange data. The API is not yet wired to this database; the existing runtime continues to use process memory. Do not describe the exchange as durable or production-ready until transactional repository integration and PostgreSQL integration tests have been completed.

## Prepare a dedicated demo database

1. Create a dedicated PostgreSQL database for the demo. Do not use a production financial database.
2. Set `DATABASE_URL` as a secret in your deployment environment or shell. Never commit credentials to Git.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run the migration explicitly with `python scripts/migrate.py`.
5. Verify the `schema_migrations` table and expected tables exist.

The runner applies numbered SQL files in order, records applied filenames, skips recorded migrations, and exits nonzero on error. It does not run automatically at application import/startup. Use a least-privilege migration account, separate from any future application runtime account.

## Important limitations

- The migration runner only creates schema; it does **not** connect API routes to PostgreSQL or seed balances.
- The current API still stores balances, orders, fills, and idempotency keys in memory.
- Do not configure a live-money feature or connect wallet keys. No deposits, withdrawals, custody, blockchain transactions, or live trading are supported.
- Before application integration, implement atomic transactions and row locking for balance reservations, matching, fills, and idempotency. Add real PostgreSQL integration tests for concurrent orders, rollback, restart persistence, and repeated idempotency keys.

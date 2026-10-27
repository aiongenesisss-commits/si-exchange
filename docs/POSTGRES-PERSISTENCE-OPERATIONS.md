# PostgreSQL persistence operations

This is an opt-in durable backend for the **simulation-only** SI Exchange demo. It does not activate live trading, deposits, withdrawals, wallet custody, payment processing, or blockchain signing.

## First-time setup

1. Provision a PostgreSQL database you control. Keep its credentials in your deployment platform's secret manager; never commit them to Git.
2. Install PostgreSQL client tools (psql) on the administration machine.
3. Set DATABASE_URL in the deployment environment, for example postgresql://USER:PASSWORD@HOST:5432/si_exchange. Use a secret, TLS, network allow-lists, and a least-privilege database role for real deployments.
4. Apply the schema explicitly from the repository root: DATABASE_URL="$DATABASE_URL" bash scripts/apply_migrations.sh.
5. Set AION_STORAGE_BACKEND=postgres and restart the application.
6. Check /health; it should report storage: postgres. If the configured database is unavailable, the app returns an unhealthy response and does not silently fall back to memory.
7. Verify /balances, /orders, /ledger, and /audit before using the demo.

On first startup, accounts A and B and their demonstration balances are inserted only when missing. Existing balances are not reset. The database transaction protects order creation, matching, balances, fills, idempotency records, and audit events as a unit.

## Switching backend

The default is AION_STORAGE_BACKEND=memory, which intentionally keeps the original test/demo behavior and loses data when the process restarts. Set the value to postgres only after applying the migration. Never use a production database for tests: the integration test truncates tables in the database named by TEST_DATABASE_URL.

## Backup and restore

Use your PostgreSQL administrator's established pg_dump / pg_restore workflow, encrypt backups, restrict access, and periodically test restoration into a separate database. Schema migrations are repeatable for the current initial schema, but production schema evolution still requires reviewed versioned migrations and rollback plans.

## Current limitations

- PostgreSQL is optional; existing deployments remain in memory mode unless explicitly configured.
- The UI market price source may use external public market data; the matching engine itself is simulated.
- This backend is an engineering/demo foundation, not audited exchange software. Do not use real funds, personal wallet keys, or customer deposits.
- The bootable OS and fully offline package repository have not yet been built or validated.

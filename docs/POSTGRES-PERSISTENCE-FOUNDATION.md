# PostgreSQL persistence foundation

## Status

This is a **schema proposal and migration foundation**, not a claim that the application currently persists data. The live demo still stores orders, fills, balances, and idempotency keys in process memory; a restart or a second serverless instance can lose or diverge from that state.

## Scope and safety boundary

- The schema is for the two existing simulated accounts only.
- All balances and fills remain simulated accounting entries.
- No real user authentication, deposits, withdrawals, custody, wallet keys, blockchain transactions, or live trading are implemented by this migration.
- Do not put private keys, seed phrases, or secrets in these tables.
- Do not set a production `DATABASE_URL` and assume persistence is active: application repository/transaction integration, migration execution, and deployment verification are separate required steps.

## Tables

- `demo_accounts`: explicitly demo-only account identities.
- `demo_balances`: simulated asset balances, stored as fixed-precision numeric values.
- `demo_orders`: limit orders and remaining quantities, with book index and database constraints.
- `demo_fills`: immutable-style execution records referencing maker/taker orders and buyer/seller accounts.
- `demo_idempotency_keys`: durable key-to-request fingerprint/order mapping, once the API is wired to it transactionally.
- `demo_audit_events`: append-oriented audit events; application permissions should deny UPDATE/DELETE for the runtime role before production use.

## Migration

The initial schema is in `migrations/001_initial_schema.sql`. Review it and run it only against a dedicated PostgreSQL database intended for this demo. Back up any existing database first. The SQL is wrapped in a transaction and uses `IF NOT EXISTS` for repeatable object creation, but it is not a general migration framework.

## Required work before calling persistence operational

1. Add a repository/transaction layer and use one database transaction for order acceptance, balance reservation, matching, fills, and audit events.
2. Lock affected balance/order rows (or use equivalent serializable/explicit locking) to prevent concurrent over-reservation across serverless instances.
3. Make idempotency insertion and order creation atomic; same key + same payload returns the original order, same key + different payload returns HTTP 409.
4. Seed only demo accounts and the explicitly documented demo balances; make seed operation idempotent.
5. Add integration tests against PostgreSQL for concurrent buy/sell reservations, partial fills, rollback, idempotent retries, and audit reconciliation.
6. Configure `DATABASE_URL` in the hosting environment using a least-privilege runtime role and a separate migration role. Never commit credentials.
7. Keep the memory-only mode clearly labelled and reject any real-money/custody feature flags.

Until these steps are complete and verified in the deployed environment, the product remains a volatile in-memory simulation. This foundation alone does not make it suitable for real funds.

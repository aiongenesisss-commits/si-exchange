# Production private API lock

## Why this exists
The current SI Exchange demo does not yet verify user identity or isolate account data by authenticated user. On managed deployments, exposing its shared demo balances, orders, order lookup, ledger, audit records, and order creation would let anonymous visitors inspect or mutate shared simulation state.

## Behavior
- On Vercel or Railway, private demo-account routes return HTTP 503 with `code=private_api_locked`.
- The same lock can be enabled locally with `AION_ACCESS_MODE=locked`.
- Public read-only health, market reference data, market-data quality, network registry, and online manifest routes remain available.
- Local development remains usable without a managed-hosting marker so the existing simulation tests and local demo workflow can continue.
- No live orders, deposits, withdrawals, custody, wallet signing, or money movement are introduced.

## Important limitation
This is a temporary fail-closed deployment gate, **not authentication**. Do not unlock private routes on a managed deployment by changing environment markers. Before private endpoints are enabled again, implement a verified OIDC/OAuth identity flow, server-derived account ownership, database-level user scoping, CSRF protection as appropriate, and cross-user isolation tests. The dashboard's private panels will not function on managed hosting while this lock is active; that is intentional until the identity boundary is real.

# SI Exchange — Authentication and Account Isolation Gate

## Status
Planning only. This document does not enable live trading, money movement, custody, wallet access, or production deployment.

## Verified risk
The current `app/main.py` exposes demo balances, orders, available balances, ledger, order details, and order creation without user authentication. The current dashboard also reads and writes those routes without an identity. This is acceptable only as an explicitly public, disposable demo; it is not an acceptable boundary for private multi-user accounts.

## Required design before private accounts
1. Keep all exchange activity simulation-only. Do not add deposits, withdrawals, signing, custody, or live orders.
2. Introduce an explicit authentication mechanism (prefer a vetted identity provider / OAuth OIDC flow for user accounts; do not invent password storage).
3. Derive account ownership from the authenticated identity on the server. Never trust a client-supplied `account=A/B` value as authorization.
4. Add ownership checks to every private endpoint: balances, available balances, orders, individual order lookup, ledger, audit, and order creation. Public endpoints must be explicitly allow-listed (health, readiness, markets, network registry, online manifest, and market-data status).
5. Migrate persistence so orders, fills, idempotency keys, and balances are scoped to a stable user/account ID. Enforce isolation in database queries and transactions, not only in the UI.
6. Protect browser mutations against CSRF where cookie-based sessions are used; set secure cookie attributes and validate origins. Apply rate limits and safe error responses.
7. Do not add a shared hard-coded API key, credentials in source, or default production credentials. If auth is not configured in a non-local deployment, fail closed rather than silently exposing private endpoints.
8. Keep demo mode usable locally through an explicit local-only setting; never let a demo fallback become a production security bypass.

## Acceptance tests
- Unauthenticated requests to all private endpoints are denied in secured mode.
- User A cannot read, mutate, or infer User B's balances, orders, fills, idempotency keys, or audit records, including by guessing IDs.
- Requests cannot switch ownership by changing `account` or other request fields.
- Repeated idempotency keys are isolated per authenticated user and request fingerprint.
- Public status and market-data endpoints remain read-only and contain no secrets.
- Missing auth configuration fails closed in deployed/secured mode.
- CI tests include at least two users and a real isolated PostgreSQL test database.
- Existing simulation-only guarantees remain true; no real financial or blockchain capability is introduced.

## Rollout order
1. Keep this plan and the market-data quality endpoint as reviewable PRs.
2. Implement auth and ownership model in a separate branch with tests.
3. Verify PostgreSQL persistence and cross-user isolation in CI.
4. Review all routes and deployment configuration.
5. Only after review and explicit approval, consider merging. Do not deploy as part of this work.

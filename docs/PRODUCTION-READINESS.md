# SI Exchange — Production Readiness Gate

Status: **NOT PRODUCTION-READY**. The deployed application is a simulation prototype, not a real-money exchange.

## Verified repository state

- The current API advertises `mode=simulation_only`, `live_trading=false`, `deposits_enabled=false`, `withdrawals_enabled=false`, and `custody_enabled=false`.
- Orders, balances, and fills are held in process memory. They are not a durable settlement ledger.
- The demo matching engine uses simulated accounts and simulated balances.
- The Binance Spot Testnet connectivity workflow previously returned HTTP 451 with a Binance eligibility/restricted-location message. This does not establish that the API credentials are invalid, and repeated retries or VPN/proxy changes are not a suitable remedy.
- No approved production exchange/custody/payment provider, production API credentials, durable ledger, or verified deposit/withdrawal reconciliation path has been established in this repository.

## Required gates before any real-money feature can be enabled

1. **Provider and eligibility:** Select a provider that explicitly supports the operator's jurisdiction and intended exchange/custody business. Obtain confirmation from that provider; do not bypass geo/eligibility restrictions.
2. **Architecture:** Separate the simulated matching engine from a provider adapter. Keep production credentials server-side in a managed secret store; never expose secrets to the browser, source code, logs, or client responses.
3. **Ledger:** Implement a durable transactional double-entry ledger, database constraints, atomic balance reservations, idempotent transaction processing, reconciliation, and immutable audit events.
4. **Trading controls:** Add authenticated users, authorization, order validation, risk/limit controls, stale-price handling, duplicate-request protection, provider order-state reconciliation, and an emergency kill switch.
5. **Deposits/withdrawals:** Integrate only a provider-approved flow with verified ownership, transaction status confirmation, replay protection, limits, sanctions/AML requirements as applicable, and operational reconciliation. Never claim a deposit is final from a client-submitted notification alone.
6. **Security and operations:** Add key rotation, least-privilege API scopes, rate limiting, CSRF/origin protections where relevant, monitoring/alerts, backups, recovery procedures, incident response, and access-controlled audit logs.
7. **Legal and launch approval:** Confirm applicable licensing, consumer disclosures, custody responsibilities, and provider terms before accepting customer funds or enabling public live trading.
8. **Release evidence:** Automated tests, security review, staging validation with provider-approved sandbox access, and a documented rollback plan must pass before a production feature flag can be enabled.

## Current operating policy

- Keep real trading, deposits, withdrawals, and custody **disabled**.
- Continue building and testing the simulation independently.
- A successful demo/testnet connection alone is not authorization or proof of production readiness.
- Do not enable production features merely by changing API flags or dashboard labels.

# AION Independent Exchange — Phase 1 Read-Only Plan

**Executive decision (2026-10-28):** Build an independent AION exchange. Phase 1 connects market-price references and account-system readiness only. No financial orders, deposits, withdrawals, custody, payment processing, blockchain signing, or movement of funds are authorized in this phase.

## Verified baseline

- The current app is an Arabic RTL FastAPI prototype, explicitly labelled simulation-only.
- `app/market_data.py` reads public Binance spot ticker data without credentials. It multiplies USDT quotes by a fixed 3.75 SAR/USDT reference; these are indicative SAR conversions, not executable SAR order-book quotes.
- AION/SAR currently has a simulated seed price and is not a verified live market quote. Do not imply that AION has a deployed token, liquidity, or a live market without verifiable evidence.
- `/balances` returns demo account balances. They are not linked to a real user account, bank, exchange account, wallet, or customer funds.
- `/ready` explicitly reports `real_money_enabled: false`, `blockchain_connected: false`, and `digital_vault_live: false`.
- PostgreSQL is optional and, when configured, currently persists demo data only. The current Vercel environment inspection did not show configured project environment variables; database connectivity for the deployed app has not been proven.
- Existing PRs #40 and #41 cover demo matching safety and PostgreSQL demo persistence tests. Both remain separate from live-money readiness and must not be represented as production financial controls.

## Phase 1 workstream

1. **Read-only market data**
   - Preserve source name, source timestamp, freshness, and whether a quote is live or a fallback.
   - Label converted prices as indicative; never describe them as executable SAR prices.
   - Show a clear unavailable/stale state instead of silently presenting a fallback as live.
   - Treat AION/SAR as unavailable until a real, independently verifiable market source exists.

2. **Account-system foundation**
   - Keep demo balances visibly separate from any future authenticated account.
   - Define account identity, authentication, roles, audit events, and data ownership before connecting any real provider.
   - Never infer or display a real balance from the demo ledger.
   - Do not request or store seed phrases, private keys, or exchange API secrets in source control or chat.

3. **Trading and money movement disabled**
   - No live order-routing adapter, deposits, withdrawals, custody, payments, wallet signing, or customer-money movement in Phase 1.
   - No production deployment of financial functionality and no real orders.
   - Any demo matching functionality remains labelled simulation-only and must not be mistaken for live trading.

4. **Required gates before any later live-money phase**
   - Reviewed threat model and independent security assessment.
   - Authenticated users, MFA, role separation, rate limiting, abuse controls, secrets management, and immutable audit trail.
   - Durable database, backup/restore drill, migration and rollback plan, reconciliation, idempotency, concurrency and failure-injection tests.
   - Provider/custody architecture and operational runbooks, incident response, monitoring and alerting.
   - Legal and regulatory review for intended markets, jurisdictions, custody, KYC/AML, consumer disclosures, and licensing.
   - Written executive approval for the specific next phase after evidence is presented.

## Acceptance criteria for Phase 1

- Market responses identify source, update time, freshness, and live-vs-fallback status.
- The dashboard never labels a simulated AION quote or demo balance as real.
- Account endpoints clearly report demo-only status unless a separately approved, authenticated provider integration is verified.
- No endpoint can place a real order or move money.
- CI covers stale/unavailable price feeds, invalid source data, account/demo separation, and fail-closed behavior.
- Deployment health and database connectivity are verified from the deployed environment, not inferred from a green preview build.

## Current status

This document records the approved direction; it does **not** claim that a real account provider, regulated trading venue, production database, custody system, or live-money service has been connected. The next engineering change should implement and test the read-only data-quality/status surface first, in a reviewed pull request, before any production promotion.

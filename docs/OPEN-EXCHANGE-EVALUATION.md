# AION-owned Exchange Architecture Evaluation

Updated: 2026-10-27

Status: **RESEARCH / DESIGN ONLY — no production engine integration in this change.**

## Objective

Build SI Exchange as a digitally operated, portable, AION-controlled software system. Prefer open standards, auditable open-source components, replaceable infrastructure, and self-hosting options over unnecessary single-vendor dependence. This is a technical independence objective, not a claim that internet-based financial activity is exempt from laws or provider terms.

## Current repository facts

- `app/main.py` implements a FastAPI Arabic RTL demo with simulated accounts A/B, in-process orders, fills, balances and idempotency cache.
- `app/market_data.py` fetches public reference prices; market data is not order execution or liquidity.
- `/health` and `/api` report simulation-only mode.
- There is no persistent transactional ledger wired into runtime, no authenticated customer identity layer, no live order-routing adapter, and no verified deposit/withdrawal/custody implementation.
- The Binance Spot Testnet connectivity workflow previously returned HTTP 451 with a provider eligibility/restricted-location response. Do not infer invalid credentials from that response and do not try to evade provider restrictions using VPN/proxies.

## Candidate infrastructure: Open Exchange

Official project: https://openexchange.dev/
Introduction: https://openexchange.dev/docs/introduction
Quick start: https://openexchange.dev/docs/quickstart
Scope and responsibilities: https://openexchange.dev/docs/scope
Source organization: https://github.com/openexch

The project documents a matching engine, order-management/risk components, an internal ledger/assets engine, operational gateway and reference UI under Apache-2.0. It currently describes itself as beta and states that an external security audit has not yet been performed.

### Fit assessment

| Capability | Current SI Exchange | Open Exchange candidate | Required AION work |
| --- | --- | --- | --- |
| Arabic RTL experience | Existing demo UI | Reference UI is a separate implementation | Keep/port AION RTL UI and use our API boundary |
| Order matching | Python in-process demo matcher | Dedicated clustered matching engine | Contract and behavior compatibility tests |
| Durable internal ledger | In-memory balances/fills | Dedicated Assets Engine and settlement flow | Verify invariants; add reconciliation and restore drills |
| Market data | Public reference-price adapter | Real-time engine market-data components | Separate reference prices from executable quotes |
| Authentication / customer accounts | No production IAM established | Integrator-owned/pluggable auth | Implement and security-review IAM |
| Custody / blockchain / fiat | Not implemented | Explicitly integrator-owned | Separate approved providers and reconciled workflows |
| Production assurance | Prototype | Beta; no external security audit disclosed | Independent review and deployment-specific tests |

## Proposed target architecture

1. **AION web client:** Arabic RTL interface; never holds provider secrets.
2. **AION API gateway:** authentication, authorization, request validation, rate limits, idempotency, audit events and a kill switch.
3. **Execution boundary:** typed provider-neutral interface for submit/cancel/query order, market metadata, fills and reconciliation. Simulation remains the default implementation.
4. **Matching and risk:** evaluate Open Exchange in an isolated staging environment; do not import or expose its admin ports publicly.
5. **Ledger:** transactional, durable accounting with atomic reservations, append-only audit trail, reconciliation, backups and tested restore.
6. **Market data:** separate read-only reference-price feed from the executable order book; show source, timestamp and stale-data state.
7. **Infrastructure portability:** versioned deployment configuration, reproducible builds, exportable data, documented restore and a second-environment deployment test.
8. **External rails:** add identity, custody, blockchain settlement, fiat/payment and provider connections only as separately scoped modules with approved access and documented controls.

## Implementation phases and acceptance criteria

### Phase 1 — isolate and specify (this branch)
- Document the current state and candidate fit.
- Keep main and the current deployed simulation unchanged.
- No production secrets, customer funds, real order routing, deposits, withdrawals or custody.

### Phase 2 — local/staging proof of concept
- Run the read-only prerequisite check first: `python3 scripts/check_open_exchange_prereqs.py`. It reports missing tools, versions, available RAM, `/dev/shm`, and Docker daemon status; it does not install software or start containers.
- The current upstream quick start requires Linux, at least 8 GB available RAM, writable `/dev/shm`, Java 21, Maven 3.9+, Go 1.25+, Node 22.22+, Python 3, Docker, and `psql`. Confirm the official quick-start page before running because requirements may change.
- Pin compatible source revisions for all Open Exchange components.
- Run the official quick start in an isolated Linux development environment with the documented prerequisites.
- Verify order lifecycle, partial fills, cancellation, insufficient-balance rejection, duplicate requests, process/leader failure, ledger conservation and restart recovery.
- Record exact source revisions, test commands, logs and known failures.
- Keep admin, OMS, database and cluster ports private; use demo authentication only on an isolated development machine.

### Phase 3 — AION integration
- Write an adapter against documented APIs rather than coupling AION business logic to engine internals.
- Add contract tests and map AION's markets carefully. The candidate's demo markets are USD-denominated; they are not automatically BTC/SAR or other SAR markets.
- Retain the current AION UI and simulated adapter until parity is demonstrated.
- Do not silently translate reference USD prices into a claim of a live SAR market.

### Phase 4 — production gate (not authorized by this evaluation)
- Complete external security assessment, load/failure/recovery drills, durable ledger reconciliation, operational monitoring, key management, incident response and rollback testing.
- Verify provider acceptance and current requirements for the actual business model and customer jurisdictions with qualified professionals.
- Require a separate explicit launch decision before any real-money execution or customer asset flow.

## Decision

**Proceed with an isolated technical proof of concept; do not merge a third-party exchange stack into the deployed app yet.** The current repo lacks the Java/Go/Node/PostgreSQL runtime topology described by the candidate's quick start, and the candidate has not had an external security audit. First demonstrate reproducible local behavior, inspect the code and license notices, and establish a tested adapter boundary. No provider has approved AION through this evaluation.

## References

- https://openexchange.dev/docs/introduction
- https://openexchange.dev/docs/quickstart
- https://openexchange.dev/docs/architecture
- https://openexchange.dev/docs/scope
- https://github.com/openexch/match

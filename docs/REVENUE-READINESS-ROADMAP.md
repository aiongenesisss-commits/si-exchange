# SI Exchange — Revenue Readiness Roadmap

## Purpose

Build a credible path from the current simulation demo to a useful, paid software product. Revenue is not guaranteed, and this roadmap makes no claim that the platform currently has paying customers, real market data, or production-grade financial infrastructure.

## Current verified baseline

- Public demo: Arabic RTL interface for simulated limit orders across 13 crypto/SAR markets.
- Two hard-coded demo accounts and simulated balances.
- Orders, fills, balances, and idempotency cache are held in process memory.
- A PostgreSQL schema foundation exists, but the API is not wired to it.
- Prices are illustrative constants, not live market quotes.
- No authentication, real deposits/withdrawals, custody, wallet keys, blockchain execution, or live trading.
- Therefore the current demo must not be sold or described as a real exchange or as managing customer funds.

## Commercial strategy: sell software value before financial execution

### Stage 1 — Validate demand with a simulation product

Offer the existing demo as a clearly labelled educational or internal-testing tool. Interview prospective users and collect written feedback before investing in expensive infrastructure.

Potential customer groups:
- educators and training providers who need a safe order-matching sandbox;
- developers who need a repeatable exchange simulator for testing;
- fintech product teams that need a white-label demo environment;
- organizations that need Arabic RTL trading-interface prototypes.

Do not claim customer demand until interviews, sign-ups, or paid pilots are evidenced.

### Stage 2 — Define a narrow paid pilot

After adding basic authentication, durable storage, monitoring, backups, and tenant isolation, test one bounded offer:
- hosted private simulation workspace;
- configurable simulated balances and markets;
- exportable order/fill audit logs;
- API access with rate limits and clear uptime/support boundaries.

Illustrative price hypotheses to test—not approved prices or existing offers:
- individual developer sandbox: $19–$49/month;
- small team sandbox: $99–$299/month;
- custom white-label pilot: scoped quote after discovery.

Use customer interviews and actual willingness-to-pay evidence to revise or reject these hypotheses. Do not advertise guaranteed returns or investment outcomes.

### Stage 3 — Reliability and security gates

Before charging for hosted access:
1. Integrate PostgreSQL transactions for order creation, balance reservation, matching, fills, idempotency, and audit events.
2. Add PostgreSQL integration tests for concurrent orders, rollback, duplicate requests, and restart recovery.
3. Add authentication, authorization, per-tenant data isolation, request limits, secrets management, backups, and restore drills.
4. Add operational monitoring and a support/incident process.
5. Clearly distinguish simulated prices from any later licensed/live market data.
6. Obtain independent security review appropriate to the intended deployment.

### Stage 4 — Only consider regulated features after specialist review

Real trading, customer assets, custody, deposits, withdrawals, token issuance, brokerage, or financial promotions are explicitly out of scope for this roadmap. Do not enable them merely by adding API keys or a database. First obtain jurisdiction-specific legal/compliance advice, licensing analysis, risk controls, and a separately approved architecture.

## Revenue measurement

Track evidence, not aspirations:
- qualified prospects contacted;
- discovery conversations completed;
- pilot proposals sent;
- paid pilots actually collected;
- monthly recurring revenue (MRR);
- churn, support cost, hosting cost, and gross margin.

Count revenue only after a payment provider confirms a completed payment and the application reconciles it. Do not count clicks, inquiries, draft invoices, simulated trades, or unconfirmed checkout events as revenue.

## Immediate next actions

1. Finish and test durable simulation persistence before offering reliability-dependent paid plans.
2. Publish a concise product page explaining simulation-only capabilities and limitations.
3. Conduct a small, no-ad-spend validation round and document actual feedback.
4. Build the smallest paid pilot around demonstrated demand rather than adding speculative features.

## Safety and spending policy

- No paid advertising, paid services, infrastructure upgrades, or other new costs without explicit approval.
- No real-money features or mainnet deployment under this roadmap.
- Never request or store wallet seed phrases or private keys.
- Never claim revenue, customers, partners, live prices, or production readiness without verifiable evidence.

# SI Exchange — Provider Options and Ownership Plan

Updated: 2026-10-27

## Executive decision

Use a two-track plan:

1. Apply to a real execution/infrastructure provider; the strongest publicly documented platform-partner lead found in this review is Kraken's API Partner Program. This is an application, not an approval or guarantee of eligibility.
2. Build AION-owned exchange software on open-source infrastructure while provider onboarding and legal/compliance review proceed. Software ownership does not itself confer regulatory approval or provide liquidity, fiat rails, custody, or bank access.

Do not enable real-money orders, customer deposits, withdrawals, or custody until provider acceptance, jurisdictional/legal clearance, security review, durable ledger integration, and release approval are complete.

## Candidate A — Kraken API Partner Program

Official page: https://www.kraken.com/institutions/api-partner
Official announcement: https://blog.kraken.com/product/api/introducing-the-kraken-api-partner-program

Publicly documented offer:
- Integrations for crypto spot, futures and tokenized equities (product and jurisdiction dependent).
- Partner qualification and onboarding are required.
- API integration and technical support are described.
- The program describes a tiered commission model for eligible new integrations.

Unknown until Kraken reviews the application:
- Whether AION's legal entity, ownership, intended users and operating jurisdictions qualify.
- Whether Kraken supports the intended user-facing model, asset availability and fiat rails.
- Contract, fee, KYC/AML, branding, custody and settlement requirements.

Decision: apply for evaluation; do not represent AION as a Kraken partner until written acceptance and contract execution.

## Candidate B — Open Exchange open-source infrastructure

Official documentation: https://openexchange.dev/docs/introduction
Source: https://github.com/openexch/match
License: Apache-2.0 (per project documentation).

Publicly documented scope:
- Matching engine, order-management/risk components, ledger infrastructure and market-data components.
- Self-hostable and modifiable open-source software.

Material limitation:
- The project describes itself as beta and says it has not had an external security audit. It explicitly leaves identity, KYC/AML, custody, fiat and regulatory compliance to the integrator.
- It is an exchange engine, not a regulated liquidity provider, bank, custodian, or fiat on/off-ramp.

Decision: suitable for a research/staging prototype and possible future AION-owned engine after technical review; not safe to receive real funds as-is.

## Candidate C — CCXT

Official documentation: https://docs.ccxt.com/about-us

CCXT is a free MIT-licensed library that unifies APIs for many exchanges. It is a connector library, not an exchange, liquidity provider, custodian, or regulatory approval. It may help implement provider adapters after the selected venue and account eligibility are confirmed.

## Saudi legal/regulatory caution

The Capital Market Authority's published warning states that virtual currencies were not regulated inside the Kingdom and that no parties or individuals were licensed for such practices by Saudi regulators in its 2018 notice:
https://cma.gov.sa/en/MediaCenter/PR/Pages/Virtual_Currencies.aspx

SAMA's in-force Implementing Regulations of the Payments and Payment Services Law set licensing requirements for relevant payment services:
https://www.rulebook.sama.gov.sa/en/implementing-regulations-payments-and-payment-services-law

These sources do not replace current advice on AION's exact business model. Before any Saudi-facing customer funds or fiat services, obtain written, current guidance from qualified counsel and the relevant regulator. Do not assume that incorporating elsewhere or using an offshore provider automatically authorizes serving Saudi residents.

## Recommended implementation sequence

1. Send a provider-partner application to Kraken and request written confirmation of entity, jurisdiction, product, fiat and customer-model eligibility.
2. Keep SI Exchange's current simulation-only service isolated from any production order-routing service.
3. In a separate branch, evaluate Open Exchange architecture and license compatibility; produce a component map and threat model before adapting it.
4. Build a provider-neutral interface for market data, order submission, order status, cancellation, fills, and account reconciliation. Never route production orders to a provider until its onboarding is approved.
5. Add durable transactional double-entry accounting, authenticated users, authorization, idempotency, audit logs, monitoring, recovery drills and a kill switch.
6. Design deposits/withdrawals only around a contractually approved custodian/payment partner. Never treat an incoming browser callback as proof of settlement.
7. Complete security review, legal/compliance sign-off and an explicit production release approval before enabling live features.

## Cost reality

Open-source code can be free. Running production infrastructure, audits, legal advice, licensing, compliance, custody, payment rails, and provider services may not be free. No provider has been verified as having approved AION or guaranteed zero-cost production access.

## Current status

- Provider approval: NOT CONFIRMED.
- Production API credentials: NOT CONFIGURED/VERIFIED.
- Real order routing: NOT IMPLEMENTED.
- Customer deposits/withdrawals/custody: NOT IMPLEMENTED.
- Current app: simulation-only.

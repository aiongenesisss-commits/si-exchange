# Real-Trading Provider Readiness Gate

## Current state (verified from the repository design)
SI Exchange is a simulation-only demo. Its balances, orders, matching and ledger are in-memory application state. Public market prices are read-only reference data; they do not route or execute orders. The existing `/orders` endpoint must not be presented as a real exchange.

## Required gates before any live order can be enabled

1. **Jurisdiction and operating model**
   - Obtain qualified legal/compliance advice for every target customer jurisdiction.
   - Determine whether the business model requires exchange, broker, custody, payments, money-services, or other permissions.
   - Do not solicit customer funds or claim the platform is licensed until independently verified.
   - For Saudi-facing operations, review current official regulator guidance and confirm the exact business model with qualified local counsel and the relevant regulator before launch.

2. **Provider approval**
   - Select a regulated, contractually approved execution/custody provider that accepts the company and intended jurisdictions.
   - Verify corporate onboarding, supported countries, supported SAR fiat rails, supported assets, fees, API terms, operational support, and incident process.
   - Confirm sandbox access first. A public market-data endpoint is not an execution provider.

3. **Security**
   - Keep provider credentials in server-side secret storage only; never commit them, return them to browsers, or ask users to paste private keys into chat.
   - Use least-privilege credentials, IP allowlists where available, withdrawals disabled, separate sandbox/production credentials, rotation, audit logging, and emergency revocation.
   - Require authentication, authorization, rate limits, CSRF protection where applicable, idempotent order submission, and per-user limits before order routing.

4. **Ledger and correctness**
   - Replace process-local balances/orders with transactional durable storage.
   - Use decimal/fixed-point arithmetic for money and quantities.
   - Atomically reserve funds, submit orders, reconcile provider acknowledgements/fills, and release reservations on cancel/reject.
   - Handle timeouts as unknown outcomes and reconcile with the provider before retrying.
   - Verify balances and executions against provider records; add concurrency, restart, duplicate-request, partial-fill, cancellation, and rollback tests.

5. **Release sequence**
   - Phase A: current simulation + public read-only market data.
   - Phase B: provider sandbox adapter, with no real credentials or real orders.
   - Phase C: external security review, operational runbooks, reconciliation and compliance sign-off.
   - Phase D: production execution only after all gates are documented and explicitly approved by the company owner and provider.

## Non-negotiable safety default
Live execution remains disabled. No production order endpoint, deposits, withdrawals, custody, wallet signing, or real-money balance is enabled by this document. Do not change this default merely because a provider API key becomes available.

## Immediate next implementation task
Build a provider-neutral execution interface and a sandbox-only adapter, then test it against a provider sandbox once a provider is selected and approved. Keep market-data fetching separate from order execution.

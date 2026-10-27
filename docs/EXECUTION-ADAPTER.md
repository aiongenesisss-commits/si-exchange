# Execution adapter — current scope

## What was added

- A provider-neutral Python protocol for submit, read, and cancel order operations.
- An in-process adapter for local simulation, with decimal-string validation, idempotency-key replay protection, and cancellation.
- A fail-closed factory controlled by `EXECUTION_MODE`. Missing configuration defaults to `simulation`; `simulation` and `sandbox` both select the local in-process adapter only.
- `REAL_TRADING_ENABLED=true` is rejected because production execution is not implemented. Unknown execution modes are rejected.

## Important boundary

This is **not** an integration with Binance, another exchange, or an external provider sandbox. It does not route orders, perform matching, hold funds, access wallets, or touch a blockchain. It is a small tested seam for future provider integration, separate from the existing demo API. The existing application continues to run its own simulation path.

## Next gates

1. Select and approve an execution provider and obtain its documented sandbox access.
2. Implement a separate provider-specific sandbox adapter and contract tests without production credentials.
3. Add authentication/authorization, durable transactional ledger and reservations, reconciliation, observability, and security review.
4. Obtain jurisdiction-specific legal/compliance clearance.
5. Keep production routing disabled until the owner explicitly approves it after all gates pass.

Never commit provider secrets or wallet keys. A successful build or market-data feed is not evidence that real order execution is available.

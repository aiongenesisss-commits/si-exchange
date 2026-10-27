# Execution adapters — current scope

## Available modes

- `EXECUTION_MODE=simulation` (default): local in-process simulation only.
- `EXECUTION_MODE=sandbox`: same local simulation adapter.
- `EXECUTION_MODE=binance_testnet`: explicit Binance Spot Testnet adapter, only when server-side `BINANCE_TESTNET_API_KEY` and `BINANCE_TESTNET_API_SECRET` are configured. This adapter hard-codes `https://testnet.binance.vision`; there is no configurable base URL and it cannot route to Binance production.
- `REAL_TRADING_ENABLED=true`: rejected. Production execution is not implemented.

## Binance testnet boundary

The adapter supports limit orders on explicit USDT spot pairs such as `BTC/USDT`. It intentionally rejects the app's SAR-denominated markets because those are not Binance spot symbols. It signs private requests, uses the exchange's client order ID field, and supports submit/query/cancel. HTTP calls are covered by mocked tests; no real external testnet order has been submitted as part of CI.

The testnet order registry is process-local, not durable. A restart can prevent lookup/cancellation by returned order ID through this adapter. This is a development bridge, not a production ledger or complete execution system.

## Credentials and setup

1. Create a Spot Testnet account and API key through the official testnet portal.
2. Store its key and secret only as server-side environment secrets:
   - `BINANCE_TESTNET_API_KEY`
   - `BINANCE_TESTNET_API_SECRET`
3. Set `EXECUTION_MODE=binance_testnet` only in a dedicated non-production test environment.
4. Do not use production exchange credentials. Do not commit secrets, put them in client-side code, or send them in chat.

Official docs:
- Spot API documentation: https://github.com/binance/binance-spot-api-docs
- Spot Testnet overview and endpoint: https://github.com/binance/binance-spot-api-docs/blob/master/testnet/general-info.md

## Before production could ever be considered

Add durable transactional order storage and reconciliation, account authorization, robust retries and unknown-outcome handling, exchange-filter validation, rate-limit handling, audit logging, concurrency/restart/partial-fill tests, independent security review, and jurisdiction-specific legal/compliance clearance. Keep production routing disabled until all gates pass and the owner explicitly approves it.

No live trading, deposits, withdrawals, custody, wallet integration, or blockchain actions are implemented here. Never claim real order execution based on a passing build or a market-data feed.

# SI Exchange demo authentication and account-isolation plan

Status: implementation gate; private managed-host APIs must remain locked.

## Safety boundary

This application is a simulation. Authentication must not enable real deposits, withdrawals, custody, signing, blockchain transactions, or live trading. Do not place credentials in source control, browser bundles, logs, screenshots, or test fixtures.

## Required design before unlocking private APIs

1. **Use a maintained identity provider** (OIDC/OAuth2) or a reviewed signed-token verifier. Do not treat a caller-supplied account name, query parameter, or unsigned header as identity. Validate signature, issuer, audience, expiry, and relevant scopes.
2. **Derive account ownership server-side.** Resolve the verified subject to an internal demo account from a server-side mapping. Ignore or reject a client-provided `account` that does not match that mapping. Never accept a user ID as proof of ownership.
3. **Scope every read and write.** Balances and available balances must return only the caller's account. Orders and order detail must be account-scoped. Ledger entries should be returned only when the authenticated subject is authorized to see the related trade. Audit endpoints must not reveal other users' identifiers, balances, orders, or fills.
4. **Keep matching atomic.** Matching may involve two authorized demo accounts, but account ownership checks must happen before order placement and persistence. PostgreSQL operations must enforce ownership inside the same database transaction, not only in route handlers.
5. **Make idempotency ownership-aware.** Scope idempotency keys by authenticated subject/account and endpoint; reject reuse with a different payload. Persist keys atomically with the order when using durable storage.
6. **Fail closed.** On managed hosting, missing or invalid identity configuration must keep private endpoints unavailable. Do not silently fall back to memory storage or unauthenticated mode. Keep the existing managed-host lock until all gates below pass.
7. **Protect the browser client.** Add a deliberate login/token flow before private API calls are enabled. Never embed a service credential in frontend JavaScript. Avoid persisting bearer tokens in local storage; prefer the identity provider's supported browser flow and short-lived tokens.
8. **Minimize audit data.** Return only the caller's scoped audit result. Keep global integrity diagnostics restricted to an operator-only path with a separate role and sanitized output.

## Required tests

- Missing, malformed, expired, wrong-issuer, wrong-audience, and invalid-signature credentials are rejected.
- Account A cannot read Account B's balances, available balances, orders, order detail, fills, or scoped audit results.
- A request authenticated as A cannot submit an order for B, even if the body says `account: B`.
- Matching transfers only the expected simulated asset and SAR quantities; unrelated assets remain unchanged.
- A user's idempotency key cannot replay or conflict with another user's order.
- Storage failure rolls back balances, orders, fills, and idempotency state.
- Concurrent orders cannot overspend reserved demo balances.
- Managed-host private endpoints remain locked when provider configuration, durable storage, or required scopes are missing.
- No test enables real money, custody, blockchain signing, deposits, withdrawals, or live trading.

## Release gates

Do not unlock the managed-host private APIs until the identity provider and account mapping are configured outside source control, the full test suite passes on the exact commit, the database transaction path is verified, and a reviewer confirms that cross-account reads are denied. Do not merge or deploy as part of this plan.

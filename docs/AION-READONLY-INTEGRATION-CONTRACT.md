# SI Exchange ↔ AION Read-Only Integration Contract

Status: **Draft — source-code reviewed; runtime contract not yet verified**
Last reviewed: 2026-10-28
Scope: read-only monitoring only. This document does not authorize deployment, account changes, order placement, real-money activity, or access to Redis/PostgreSQL.

## 1. Evidence and current boundary

Reviewed source:
- `app/main.py` on `main`: FastAPI app metadata version `0.1.0`; route definitions for `/api`, `/health`, `/ready`, `/production-readiness`, and `/markets`.
- `app/redis_store.py`: internal Redis state persistence; not an integration API.
- AION repository `docs/SI-INTEGRATION.md`: no provider-supported SI API endpoint or authentication scheme was verified as of 2026-10-19.

Production Railway service and domain are known, but live HTTP responses and the effective storage selection have not yet been independently verified. Route definitions below are **code-defined contracts**, not claims that each route has been successfully called in production.

## 2. Existing read-only routes (source-defined)

Base URL for the current Railway service:
`https://si-exchange-production.up.railway.app`

| Method and path | Purpose | Source-defined response | Side effects |
|---|---|---|---|
| `GET /api` | Product capability summary | `name`, `mode`, `live_trading`, `deposits_enabled`, `withdrawals_enabled`, `custody_enabled` | None in handler |
| `GET /health` | Process/storage connectivity probe | `status`, `mode`, `storage` | Redis/PostgreSQL ping when configured |
| `GET /ready` | Readiness and capability flags | `status`, `mode`, `storage`, `durable_demo_storage`, `real_money_enabled`, `blockchain_connected`, `digital_vault_live` | Redis/PostgreSQL ping when configured |
| `GET /production-readiness` | Explicit blockers for production readiness | `status`, `mode`, `checks`, `blockers`, `note` | None in handler |
| `GET /markets` | Market list with source and simulation flags | Array of market records including `symbol`, `simulated_price_sar`, `is_live`, `price_source`, `updated_at`, `trading_mode` | May read an external market-data source |

These paths are defined in `app/main.py`. Do not interpret `/ready` or `durable_demo_storage: true` alone as proof of restart persistence, backups, authentication, or production readiness. `/production-readiness` explicitly reports missing authentication and per-user account isolation.

## 3. Authentication and authorization

- Current source does not define authentication for the read-only routes above. Treat them as public endpoints and return no secrets or user-specific data from the AION poller.
- No AION service credential, API key, signed-request scheme, or OAuth scope is currently defined by this contract.
- Do not send credentials in URLs. Do not read or write Redis directly from AION.
- Private paths such as `/balances`, `/available-balances`, `/orders`, `/ledger`, and `/audit` are intentionally locked by middleware on managed deployments until verified authentication and account isolation are implemented. Do not make AION depend on them.
- No order-writing permission is granted. `POST /orders` is out of scope and must not be called by AION.

## 4. Suggested normalized monitoring record (AION-side proposal, not an existing endpoint)

AION should store a poll result as a timestamped evidence record, without inventing a combined health status:

```json
{
  "contract_version": "draft-1",
  "service": "si-exchange",
  "checked_at": "RFC3339 timestamp",
  "source_endpoint": "/ready",
  "http_status": 200,
  "response": {
    "status": "ready",
    "mode": "simulation_only"
  },
  "verification_level": "http_response_observed"
}
```

This is an AION-side record shape only. It is not a response schema emitted by SI Exchange.

## 5. Errors, timeouts, rate limits, and logging

- Source-defined dependency failure: `/health` and `/ready` return HTTP 503 when configured Redis/PostgreSQL connectivity checks fail.
- HTTP client timeout: proposed AION poller default is 3 seconds per request; retry at most twice with exponential backoff and jitter, then record the check as `unknown`. This is a proposed client policy, not a provider guarantee.
- Rate limit: no documented limit or `429` contract was found in the reviewed application source. Poll conservatively (suggested 60-second interval) and add a local cap; confirm limits before increasing frequency.
- Logging: log timestamp, endpoint, HTTP status, elapsed time, and a request/correlation ID if available. Never log URL credentials, authorization headers, environment variables, response secrets, or raw database/Redis errors.
- Versioning: FastAPI metadata currently says `0.1.0`; the routes are not namespaced under `/v1`. Do not assume backward compatibility. Add schema/contract tests before changing response fields.

## 6. Compatibility tests required before enabling polling

1. Contract tests for each approved GET route using recorded, redacted fixtures.
2. Validate HTTP status, content type, required fields, field types, and simulation-only flags.
3. Verify dependency outage maps to an explicit unavailable state; do not convert errors into healthy.
4. Verify unknown/new response fields are tolerated but required-field removal fails the compatibility test.
5. Verify no polling path can invoke `POST /orders` or access private account routes.
6. Verify logs contain no credentials or secret values.
7. Run first against a test/staging target; only then allow low-frequency production GET polling after owner approval.

## 7. Proposed next API improvement (not implemented here)

Add a dedicated read-only `GET /integration/v1/status` endpoint with a documented JSON schema, explicit contract version, bounded dependency checks, and stable error codes. Keep authentication optional only if all returned fields are intentionally public; otherwise require a narrowly scoped read-only credential. This endpoint must never expose balances, orders, ledger rows, internal hostnames, secrets, or raw exception messages.

## 8. Acceptance state

- Source inspection of the route definitions: **PASS**.
- Live production HTTP contract checks: **NOT RUN / BLOCKED** (direct runtime response not yet obtained).
- Redis actually selected in production: **UNKNOWN** (Railway variable values are redacted to this review).
- Restart persistence and backup recovery: **NOT RUN**.
- SI provider API integration: **BLOCKED** until official provider API documentation and permission are supplied.
- Production changes: **NONE**.

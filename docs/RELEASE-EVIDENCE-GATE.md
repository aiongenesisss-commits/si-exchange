# SI Exchange release evidence gate

## Purpose

The `Release Evidence Gate` workflow runs the full test suite against disposable PostgreSQL 16 and Redis 7 services, including integration tests when the repository's test suite is configured to use `TEST_DATABASE_URL` and `TEST_REDIS_URL`. It emits a `release-evidence.json` artifact bound to the exact GitHub candidate SHA and workflow run.

## Acceptance rule

A candidate passes this CI gate only when the workflow's `Enforce release gate` job succeeds and the artifact reports the same `candidate_sha` as the commit being considered. The artifact records CI test outcome and that test services were ephemeral. It does **not** claim that production uses those services or that a deployment succeeded.

Before calling a release deployed, an operator must independently verify all of the following:

1. The production deployment's source commit SHA exactly equals the accepted candidate SHA.
2. The production health/readiness check succeeds after deployment.
3. The deployed service's configured persistence backend is identified and an actual connection/read-write health check succeeds without exposing credentials.
4. The managed-host private API lock remains in force until verified authentication and per-user authorization are implemented and tested.

## Current limitations

- The existing `/production-readiness` endpoint reports configured PostgreSQL settings, not a live database connection test.
- A green CI run is not proof of production deployment or production persistence.
- The current Vercel free daily deployment cap can block deployments; do not upgrade automatically or treat a rate-limit failure as a test failure.
- Keep the application simulation-only. Do not enable real deposits, withdrawals, custody, live orders, or blockchain transactions.

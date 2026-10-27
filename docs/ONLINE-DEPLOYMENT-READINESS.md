# SI Exchange — Online Deployment Readiness

## What this configuration does

- Builds the service from the repository's Dockerfile.
- Uses `GET /ready` as the deployment health check.
- Restarts a failed process up to ten times.
- Keeps the service in simulation-only mode; it does not add wallet, blockchain, deposit, withdrawal, custody, or live-trading functionality.

The Railway configuration is deployment metadata only. It does not create a Railway project/service, provision hosting, create a database, or prove that a public deployment is live.

## Required environment settings

### Demo-only deployment (volatile)

- `AION_STORAGE_BACKEND=memory` (or leave unset).
- This is suitable only for a demo. Orders and balances reset when the process restarts, and multiple replicas do not share state.

### Persistent demo deployment

Before enabling PostgreSQL mode, provision an approved PostgreSQL service and set:

- `AION_STORAGE_BACKEND=postgres`
- `DATABASE_URL` to the database's private connection URL, stored as a secret.

Apply the checked-in schema using `bash scripts/apply_migrations.sh`, then restart the app and verify:

1. `GET /health` reports `storage: postgres`.
2. `GET /ready` reports `durable_demo_storage: true`.
3. `GET /audit` reports `valid: true`.
4. A test order survives a restart and is still marked as simulation data.

Do not place database URLs, API tokens, wallet private keys, or recovery phrases in source files, logs, issues, or chat.

## Release gates before public use

- Confirm the hosting provider, account owner, service, domain, and budget.
- Confirm PostgreSQL backups, restore test, access restrictions, and retention.
- Add rate limiting and abuse protection at the edge.
- Run dependency and container vulnerability scans.
- Test concurrent order placement and reconciliation.
- Publish a privacy notice and operational contact.
- Keep all real-money features disabled until a separate legal, security, custody, and operational review is complete.

## AION infrastructure truth table

The API's `/online-manifest` is the public inventory for this application. A green health check means only that the service and its configured storage respond. It does not prove that AION Nova or AION Orbit exists as a live blockchain, that AION Coin is deployed, or that a digital vault holds assets.

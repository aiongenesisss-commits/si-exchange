# SI Exchange online deployment foundation

Status: deployment configuration committed for review; this file alone does not create a hosted service or configure DNS.

## Container deployment

The repository includes a Dockerfile. The intended container command is:

```sh
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

The health check is `/health`. After a deployment, verify all of the following against the actual public URL:

- `GET /health` returns HTTP 200.
- `GET /ready` accurately reports the configured storage mode.
- `GET /online-manifest` describes the deployed build and service paths.
- `GET /audit` passes its invariants.
- The Arabic RTL dashboard loads on desktop and mobile.

## Persistence

The default in-memory mode is a demo and loses orders, fills, and balances when the process restarts. For durable demo data, provision PostgreSQL and set these variables in the hosting provider's secret/environment settings:

- `DATABASE_URL` — private database connection URL (secret).
- `AION_STORAGE_BACKEND=postgres`.

Do not put credentials in source control. If PostgreSQL mode is requested but the database is unavailable, the app is designed to fail closed rather than silently use memory. Test migrations and backup/restore before relying on persistence.

## Product boundary

This remains a simulated exchange. Deployment configuration does not add real deposits, withdrawals, custody, wallet-key management, blockchain settlement, or live trading. The seeded AION/SAR quote and balances are simulation values, not a verified market price, token contract, or customer funds.

## AION Nova / AION Orbit

These are separate chain infrastructure projects, not something a web-app deployment can create by itself. Each requires supported EVM client software, genesis and consensus configuration, persistent nodes, RPC security, monitoring, explorers, and a funded gas sponsor for the first-50-free-deployments offer. Do not publish RPC endpoints or claim either chain is live until those services are deployed and independently checked.

## Cost and security gate

Do not provision paid infrastructure or turn on billable services without explicit budget authorization. Before production financial use, require an independent security review, access controls, durable database and backups, incident response, rate limits, monitoring, and documented recovery procedures.

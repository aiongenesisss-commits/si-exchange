# SI Exchange — portable online deployment

This repository contains a Dockerfile, a hardened Docker Compose runner for a prebuilt image, and a GitHub Actions workflow that runs tests and builds the image. These are portable deployment assets; they do **not** prove that a self-hosted server has been provisioned.

## Verified online service

- Public demo: https://si-exchange-1vq1.vercel.app/
- Source repository: https://github.com/aiongenesisss-commits/si-exchange
- The current public app host is Vercel. The application is a **simulation-only demo**.
- No real deposits, withdrawals, custody, wallet signing, blockchain settlement, or live trading are enabled.
- AION Nova and AION Orbit are proposed networks, not running public networks.

## Run the container locally or on a Linux host

Requirements: Docker Engine and the Docker Compose plugin.

1. Build the image from the repository root:
   `docker build -t si-exchange-linux:local .`
2. Start the app:
   `docker compose up -d`
3. Check the local app:
   `curl -fsS http://127.0.0.1:8000/health`
   `curl -fsS http://127.0.0.1:8000/audit`
4. Inspect logs: `docker compose logs --tail=100 si-exchange`
5. Stop it: `docker compose down`

Compose binds the app to `127.0.0.1:8000`, runs with a read-only root filesystem, drops Linux capabilities, and enables `no-new-privileges`. It does not start PostgreSQL and does not make the service publicly reachable by itself. Put a self-hosted instance behind a properly configured TLS reverse proxy before exposing it to the internet.

## Optional PostgreSQL persistence for demo data

The app has an opt-in PostgreSQL backend for **demo-only** balances, orders, fills, idempotency records, and audit events. It is not enabled by the default Compose file. To use it, provision a PostgreSQL database on a private network, set `DATABASE_URL` as a secret, apply `migrations/001_initial_schema.sql` with the provided migration script, set `AION_STORAGE_BACKEND=postgres`, and verify `/health` and `/audit`. Do not expose PostgreSQL publicly. Take and test backups before upgrades.

## Before public self-hosting

- Configure a firewall, TLS, security updates, monitoring, backups, and a recovery contact.
- Keep credentials outside source control and rotate any exposed secrets.
- Verify health, audit results, and a backup restore after deployment.
- Do not use this demo database as a real-money ledger or customer account system.

## Ownership and cost boundary

The code and deployment configuration are in the GitHub repository. Hosting accounts, domain registration, DNS, and cloud infrastructure remain separate provider-controlled resources; code in this repository does not transfer them into AION's ownership. A continuously online self-hosted instance requires an always-on host and may incur fees. This documentation does not provision a server or authorize spending.

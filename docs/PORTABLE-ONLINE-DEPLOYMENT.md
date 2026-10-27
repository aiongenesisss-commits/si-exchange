# SI Exchange — portable online deployment

This repository now includes a Docker image, a Docker Compose deployment with PostgreSQL persistence, and CI that tests the simulation and builds the image. These are deployment assets, not proof that a self-hosted server has been provisioned.

## What is actually online

- Public demo: https://si-exchange-1vq1.vercel.app/
- Source: https://github.com/aiongenesisss-commits/si-exchange
- Vercel is the current public app host. The application is a **simulation-only demo**.
- No real deposits, withdrawals, custody, wallet signing, blockchain settlement, or live trading are enabled.
- AION Nova and AION Orbit are separate proposed networks; neither is running publicly yet.

## Run the portable stack on a Linux host

Requirements: Docker Engine and the Docker Compose plugin. Use a host you control and a firewall that only exposes the app's intended public port. PostgreSQL is bound to a private Docker network and is not published to the internet.

1. Clone this repository on the host.
2. Set a strong unique database password in the host environment; do not commit it:
   `export POSTGRES_PASSWORD='replace-with-a-long-random-secret'`
3. Optionally choose the app port (default 8000):
   `export SI_EXCHANGE_PORT=8000`
4. Start the stack:
   `docker compose up -d --build`
5. Verify:
   `curl -fsS http://127.0.0.1:8000/health`
   `curl -fsS http://127.0.0.1:8000/audit`
6. Check logs with `docker compose logs --tail=100 app db`; stop with `docker compose down`.

The database volume persists demo balances, orders, fills, idempotency records, and audit events across restarts. The initial SQL migration is applied automatically only when PostgreSQL initializes a new empty data directory. Back up the volume before upgrades and apply later migrations explicitly.

## Before exposing it to the public internet

- Put the app behind a TLS reverse proxy or managed HTTPS endpoint; do not expose PostgreSQL.
- Use a firewall, security updates, backups, monitoring, and an incident-response contact.
- Replace placeholder secrets and manage them outside source control.
- Run restore drills and verify `/health` and `/audit` after deployment.
- Do not use this demo database as a real-money ledger or customer account system.

## Ownership and cost boundary

The source and deployment configuration are version-controlled in AION's GitHub repository. Public hosting and a domain are separate provider-controlled resources; this commit does not transfer provider infrastructure or register a custom domain. A continuously online self-hosted instance needs a server with reliable uptime and may incur fees. No server or paid service is provisioned by these files, and no spending is authorized.

# Self-hosted SI Exchange stack

This is a deployment recipe, not a claim that a server has already been provisioned. It runs the SI Exchange application, PostgreSQL database, and HTTPS gateway together on a server controlled by AION.

## What AION controls

- Application source and deployment configuration remain in the AION-controlled GitHub repository.
- PostgreSQL data is stored in the persistent `si_exchange_pgdata` volume on the chosen server.
- The database is on a private Docker network and is not published to the public internet.
- Caddy terminates HTTPS and forwards requests to the application.
- The app explicitly runs with `AION_STORAGE_BACKEND=postgres`; it must not silently fall back to memory storage.

## Prerequisites

1. A Linux server with Docker Engine and the Docker Compose plugin installed.
2. A domain controlled by AION, with DNS A/AAAA records pointing to the server.
3. Inbound TCP ports 80 and 443 permitted by the server firewall.
4. AION-approved hosting budget. This stack is self-managed software, but a public server, domain registration, connectivity, and backups may incur third-party costs.

## Start

From this directory:

1. Copy `.env.example` to `.env`.
2. Replace the example domain/email and generate a long random database password. Do not commit or send the `.env` file.
3. Confirm DNS points to this server before starting the gateway.
4. Run `docker compose up -d --build`.
5. Verify `docker compose ps` shows database healthy and all services running.
6. Visit `https://YOUR_DOMAIN/health`, then `/audit`, `/markets`, `/balances`, `/orders`, and `/ledger`.
7. Verify the health response reports PostgreSQL storage. If it does not, stop and investigate rather than treating the service as persistent.

The SQL schema is mounted into PostgreSQL's initialization directory and runs only when the data volume is first created. If an existing database volume is already present, apply a reviewed migration manually; do not delete the volume to force initialization.

## Important safety limits

- SI Exchange remains a **simulation-only** exchange. This deployment does not enable real deposits, withdrawals, custody, wallet signing, or live trading.
- This stack does not create a blockchain, deploy AION Coin, create a wallet, or provide a gas sponsor.
- Do not publish the database port. Keep backups encrypted and off-host, and test restoration.
- Before production use, add monitored backups, restore drills, host patching, access controls, resource limits, dependency/image pinning, incident response, and a security review.
- Do not provision paid infrastructure or purchase a domain without explicit budget approval.

## Useful commands

```bash
docker compose ps
docker compose logs --tail=100 app database gateway
docker compose exec database pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"
docker compose down
```

`docker compose down` preserves the named database volume. Never use `docker compose down -v` unless you intentionally want to delete the stored demo data.

# Public Online Services — Ownership and Readiness Register

Last updated: 2026-10-27

This register distinguishes services that have a known public URL from systems that are only planned. A public URL is not proof that every feature is production-ready.

## Known public applications

| Service | Public URL | What can be claimed | What must not be inferred |
|---|---|---|---|
| AION AUTONOMOUS website / API | https://aion-production-fbf3.up.railway.app/ | Public application URL is recorded in the AION repository | Every department is running, all APIs are healthy, or all products are ready |
| SI Exchange | https://si-exchange-1vq1.vercel.app/ | Public simulation-only exchange demo; API includes /health, /api, /markets, /balances, /orders, /ledger, /audit | Live trading, real deposits/withdrawals, custody, or real AION liquidity |
| SI Exchange source | https://github.com/aiongenesisss-commits/si-exchange | Separate source repository for the demo | A connection to TheSuperIntelligence.SI or an undocumented SI API |
| AION source | https://github.com/AION-AUTONOMOUS/AION | Public engineering repository | Proof that all planned services are deployed |

## Automated public checks

Workflow: [Public Service Health Monitor](../.github/workflows/public-service-health.yml)

It runs hourly and can be triggered manually. It checks HTTP responses from SI Exchange health/safety/audit endpoints and the public AION website/Earth API. Each run writes a concise GitHub Actions summary. A successful HTTP response proves only endpoint reachability at that time; it does not prove financial, security, data-quality, or product readiness.

## Not yet verified as live

- AION Nova and AION Orbit independent EVM networks, validator/consensus infrastructure, public RPC endpoints, explorers, faucets, and gas sponsorship.
- AION Coin contract deployed and verified on either proposed network or on BNB Smart Chain testnet.
- Production digital vault / custody. No seed phrase or private key should be uploaded to GitHub or sent in chat.
- Durable production storage for SI Exchange. Its optional PostgreSQL mode requires a database under owner control, secret configuration, migrations, backups, and a verified health response reporting `storage: postgres`. Do not assume it is configured on the public deployment.
- A documented and authenticated developer API for TheSuperIntelligence.SI; do not invent an endpoint or claim a connection without official documentation and a successful test.

## Rules for bringing additional services online

1. Prefer separate, version-controlled services with documented owners, health checks, logs, backups, and rollback procedures.
2. Keep credentials in the host's secret manager. Never commit API keys, database URLs, private keys, recovery phrases, or wallet seed phrases.
3. Keep demo systems separate from real-money infrastructure.
4. Do not enable real deposits, withdrawals, custody, token sales, or live trading without security review, legal/provider readiness, operational monitoring, and explicit budget approval.
5. Do not provision paid infrastructure or third-party services without explicit approval of the cost.
6. Publish an address or claim "live" only after checking the running service and recording evidence.

## Next implementation gates

1. Get the public health monitor passing on the actual deployed endpoints.
2. Configure and verify SI Exchange persistent PostgreSQL storage if the owner has an approved database available; keep demo mode explicit.
3. Fix the existing BNB testnet deployment secret privately in GitHub Actions; do not expose it in chat. A valid EVM private key is 32-byte hexadecimal, optionally prefixed with `0x`; it is not a wallet address.
4. Build and test Nova and Orbit as isolated devnets in CI before provisioning public validators and RPC infrastructure.
5. Add the token only after chain health, explorer verification, key custody, and supply/permissions checks pass.

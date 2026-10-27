# AION online systems — implementation and launch gates

Updated: 2026-10-27

## Current verified scope

SI Exchange is a publicly hosted, simulation-only web application. Its public deployment does not prove that the AION blockchain networks, coin contract, or a real-asset digital vault exist.

The application exposes:
- `/` — Arabic RTL dashboard
- `/health` — process and configured storage health
- `/ready` — readiness probe; reports whether configured PostgreSQL storage is reachable
- `/online-manifest` — public inventory distinguishing available demo functions from planned or disabled systems
- `/markets`, `/balances`, `/orders`, `/ledger`, `/audit` — simulated market and accounting endpoints

## Target online architecture

1. **Public web layer:** SI Exchange dashboard and documented API behind HTTPS, with rate limits and security headers.
2. **Application/API layer:** authenticated administrative routes, schema validation, audit logging, request limits, and health/readiness probes.
3. **Durable database:** managed PostgreSQL with encrypted connections, backups, restore drills, migrations, and least-privilege credentials. Demo mode must remain clearly marked until this is configured and verified.
4. **AION Nova / AION Orbit:** separate EVM-compatible networks, each with its own genesis configuration, chain ID, validator/consensus configuration, RPC endpoints, monitoring, and explorer. Proposed IDs are 71101 and 71102; check chain-ID conflicts before public release. They are not live merely because they appear in configuration or documentation.
5. **AION Coin:** audited contract source, reproducible build, testnet deployment, verified bytecode/source, and independently recorded chain ID + contract address + deployment transaction before any status is labelled deployed.
6. **Digital Vault:** start as a non-custodial interface and encrypted metadata vault. Never collect seed phrases. Do not add server-side private-key custody without a separately reviewed threat model, key-management design, access controls, incident plan, and independent audit.
7. **First 50 free deployments:** a sponsor/relayer must pay actual network gas. Implement only after a funded budget is explicitly approved, with per-network quota accounting, anti-abuse limits, monitoring, and a hard stop after the defined quota. “Free” to a user does not mean gas is free.
8. **Operations:** CI tests, dependency/security scans, uptime monitoring, alert routing, backups, recovery exercises, and a public status page.

## Release gates

- No real deposits, withdrawals, custody, bridging, or live trading while the corresponding security and legal reviews are incomplete.
- No paid hosting, paid RPC, gas sponsorship, or other spend without explicit budget approval.
- A public chain launch requires independent RPC checks from outside the host, block production evidence, restart/recovery tests, explorer visibility, and published network parameters.
- A token deployment is only verified when its transaction receipt succeeds and the address/chain ID can be independently queried on the relevant explorer.
- The online manifest must not call a planned component live.

## Safe next implementation sequence

1. Keep the public readiness and manifest endpoints truthful.
2. Add automated tests for readiness and manifest semantics.
3. Establish reproducible local EVM devnets in CI before public validators or paid infrastructure.
4. Validate genesis and chain IDs, then launch public nodes only after infrastructure and operating costs are approved.
5. Deploy AION Coin to test networks; record independently verifiable addresses and transaction hashes.
6. Implement the free-deployment sponsor only after quota definition, funding, anti-abuse design, and monitoring are approved.

## Secrets

Store credentials only in the hosting provider's secret manager or GitHub Actions secrets. Never commit secrets or paste private keys, seed phrases, or wallet recovery material into issues, source files, logs, or chat.

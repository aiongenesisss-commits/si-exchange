# AION Nova + Orbit local development networks

**Status: local development only.** This Compose stack runs two disposable Anvil EVM chains. It does not create public networks, persistent ledgers, validators, explorers, bridges, or a production RPC service. The chain IDs are proposals and must be checked for collisions before any public release.

## Requirements

- Docker Engine and Docker Compose plugin
- No wallet seed phrase, private key, or production secret is needed

## Start

From the repository root:

```sh
docker compose -f infra/aion-devnets/docker-compose.yml up -d
docker compose -f infra/aion-devnets/docker-compose.yml ps
```

RPC endpoints are bound to loopback only:

- AION Nova development RPC: `http://127.0.0.1:18545` (chain ID 71101)
- AION Orbit development RPC: `http://127.0.0.1:18546` (chain ID 71102)

Check each chain with Foundry's `cast` command:

```sh
cast chain-id --rpc-url http://127.0.0.1:18545
cast chain-id --rpc-url http://127.0.0.1:18546
```

Expected outputs are `71101` and `71102`. If Foundry is not installed on the host, use the container's `cast` binary or inspect the Compose health checks.

## Stop

```sh
docker compose -f infra/aion-devnets/docker-compose.yml down
```

Anvil state is disposable and is not persisted. Never send real assets to these endpoints. Never expose these RPC ports publicly: Anvil development accounts are unlocked and test-only.

## Before public testnet/mainnet

1. Decide the consensus/client stack and threat model; select and pin audited client versions.
2. Validate chain IDs, native gas asset, genesis parameters, validator governance, peer discovery, bootnodes, and upgrade policy.
3. Provision persistent, monitored infrastructure in at least multiple failure domains; budget and approve all recurring costs first.
4. Configure RPC rate limits, allowlists where appropriate, DDoS protection, secrets management, backups, alerting, and incident response.
5. Publish verified genesis/configuration hashes, chain metadata, explorer, faucet policy, and status page.
6. Run independent security review and reproducible deployment tests.
7. Deploy the AION token only after chain IDs and genesis are finalized, contract tests pass, and deployment authority approves. Publish verified contract addresses and transaction hashes.
8. Implement the first-50-free deployment program as an auditable, capped gas sponsorship service. Define whether the limit is 50 total or 50 per network, eligibility, anti-abuse controls, sponsor wallet limits, and stop conditions. Never promise free transactions without funded sponsorship.

## Production service naming (proposed)

AION may operate its own branded services—**AION RPC**, **AION Explorer**, **AION Vault**, **AION Identity**, **AION Monitor**, and **AION Developer Portal**—but a new name alone does not make an external service owned by AION. Ownership requires controlled infrastructure, accounts, code/license rights, security operations, and documented access. Prefer open-source components that AION can deploy and maintain, and disclose any external providers.

## Safety constraints

- No mainnet deployment or real-money transactions from this local stack.
- No real deposits, withdrawals, custody, or bridges.
- No private keys or recovery phrases in Git, issues, logs, or chat.
- Do not expose local RPC endpoints to the public internet.
- No paid infrastructure provisioning without explicit budget approval.

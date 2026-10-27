# AION Nova + AION Orbit local EVM development nodes

> **Development-only.** These Anvil nodes are disposable local test chains, not public networks. They use publicly known development keys and must never hold real assets or be exposed to the internet.

## Start

Requires Docker Compose v2.

```sh
docker compose -f infra/devnet/docker-compose.yml up -d
python3 infra/devnet/check_rpc.py
```

RPC endpoints are bound to loopback only:
- AION Nova (chain ID 71101): http://127.0.0.1:18545
- AION Orbit (chain ID 71102): http://127.0.0.1:18546

Each node has its own state. A block mined on Nova must not appear on Orbit. These chain IDs are provisional and must be checked for collisions before any public deployment.

## Stop and reset

```sh
docker compose -f infra/devnet/docker-compose.yml down
```

Anvil state is ephemeral; restarting the containers resets the chains. Do not add real private keys, seed phrases, production RPC credentials, or funded wallets to this directory.

## Before a public testnet

This scaffold is not a substitute for a production chain. A public rollout still needs a selected and version-pinned EVM client, a reviewed consensus/validator topology, persistent storage, independent RPC endpoints, TLS and rate limits, monitoring/alerting, explorer/indexer, faucet controls, key management, incident response, and a documented budget. A first-50-free contract offer also needs a funded, rate-limited gas sponsor and a transparent cap. No public nodes or paid resources are created by this scaffold.

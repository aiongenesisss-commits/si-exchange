# AION Nova and Orbit — local devnets

This is a **local development harness only**. It does not create public networks, validators, explorers, faucets, persistent storage, or production-grade consensus. Do not send real funds or reuse real wallet keys.

## Requirements

- Docker Engine
- Docker Compose v2

## Start

From this directory:

```sh
docker compose -f compose.yaml up -d
docker compose -f compose.yaml ps
```

RPC endpoints on the host:

| Network | Chain ID | RPC |
| --- | ---: | --- |
| AION Nova (local only) | 71101 | http://127.0.0.1:8545 |
| AION Orbit (local only) | 71102 | http://127.0.0.1:8546 |

Check each chain ID using Foundry's `cast` command:

```sh
cast chain-id --rpc-url http://127.0.0.1:8545
cast chain-id --rpc-url http://127.0.0.1:8546
```

Expected outputs are `71101` and `71102`, respectively.

## Stop

```sh
docker compose -f compose.yaml down
```

The chains are ephemeral; restarting them resets their state. Anvil prints public test accounts and private keys to its logs. These are disposable local test keys only and must never be used for real assets.

## Important launch gates

Before calling either chain public or deploying AION Coin, implement and test independent network genesis/configuration, supported production consensus and validators, persistent hosting, secure public RPC limits, monitoring, explorer and source verification, faucet controls, and a funded gas sponsor for any free-deployment promotion. Verify chain ID uniqueness before public launch. Do not expose these Anvil instances directly to the internet.

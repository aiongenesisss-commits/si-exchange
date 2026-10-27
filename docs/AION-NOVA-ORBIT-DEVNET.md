# AION Nova + AION Orbit — Dual EVM Devnet

**Status: isolated development scaffold only. This does not create public blockchains.**

The repository now defines two separate local EVM development nodes:

| Network | Proposed chain ID | Local JSON-RPC |
|---|---:|---|
| AION Nova | 71101 | http://127.0.0.1:18545 |
| AION Orbit | 71102 | http://127.0.0.1:18546 |

These IDs are proposals and must be checked for collisions before any public launch. The nodes are independent disposable Anvil development chains. They are not BNB Smart Chain, do not inherit BNB Chain security, and do not provide public persistence or decentralized consensus.

## Start locally

Requires Docker Engine and Docker Compose:

```sh
docker compose -f infra/aion-networks/docker-compose.yml up -d
python3 scripts/check_aion_networks.py
docker compose -f infra/aion-networks/docker-compose.yml down
```

The compose file binds ports to loopback only. Do not change this to public interfaces for an internet launch.

## Automated check

GitHub Actions workflow `.github/workflows/aion-dual-devnet-smoke.yml` starts both nodes and verifies `eth_chainId` using a read-only JSON-RPC request. A passing workflow proves only that the temporary CI nodes respond with the expected chain IDs; it does not prove that a public network exists.

## Required before internet/public launch

1. Choose and operate a production-grade EVM client and consensus model for each chain.
2. Provision persistent, monitored infrastructure and independent validators/bootnodes as appropriate.
3. Secure public RPC endpoints with rate limits, abuse protection, monitoring, backups, and incident response.
4. Publish and verify chain metadata, RPC URLs, explorers, faucet policy, and support/uptime status.
5. Implement and independently test the first-50 free deployment gas sponsor, hard spending caps, and abuse controls.
6. Audit the AION token contract and deployment process; keep keys in managed secrets and never commit or share private keys.
7. Deploy AION only after both networks pass the production gates and the token contract is reviewed. Record chain ID, RPC, explorer, contract address, transaction hash, and source commit for each deployment.

**Cost control:** no paid cloud resources are created by this scaffold. Public, persistent networks require infrastructure and ongoing operating costs; do not claim the networks or token are live until there is verifiable deployment evidence.

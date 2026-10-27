# AION Nova and AION Orbit — local EVM development networks

This folder starts two isolated **local development chains** using Anvil (Foundry). It does not launch public networks.

| Network | Proposed chain ID | Local RPC |
|---|---:|---|
| AION Nova | 71101 | http://127.0.0.1:18545 |
| AION Orbit | 71102 | http://127.0.0.1:18546 |

## Run

Requirements: Docker Engine and Docker Compose v2.

```bash
docker compose -f infra/aion-networks/docker-compose.yml up -d
```

Check each chain:

```bash
curl -sS -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' http://127.0.0.1:18545
curl -sS -H 'content-type: application/json' --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' http://127.0.0.1:18546
```

Stop and remove local demo state:

```bash
docker compose -f infra/aion-networks/docker-compose.yml down -v
```

The CI workflow starts both chains, confirms their RPC chain IDs differ as configured, and tears them down. Anvil accounts and keys are development-only and must never be reused for public networks or real assets.

## Not production

These are single-node local test chains. They have no independent validators, public bootnodes, public RPC, explorer, bridge, production consensus, security monitoring, or production persistence guarantees. Chain IDs are provisional and must be checked before any public launch. Do not describe either network as live or production-ready.

## First 50 free deployments

The free-deployment program is not active yet. A real public program requires an audited gas sponsor/relayer or protocol-level subsidy, a durable cross-replica counter, abuse controls, per-user limits, and a hard funding cap. Define whether the 50 deployments are shared across both networks or 50 per network before activation. No paid infrastructure is provisioned by these local files.

## AION token

Do not deploy the production token from this local setup. First review the exact token source and ownership controls, run tests, deploy only a clearly labeled test token to the local chains, then establish public network operations and security review. Public AION token addresses must be recorded only after on-chain transaction receipts and explorer verification exist.

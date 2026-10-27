# AION Nova and AION Orbit — local devnet foundation

## Current status

This repository now contains a reproducible local smoke-test setup for two temporary Anvil EVM development chains:

| Network | Chain ID | Local RPC |
| --- | ---: | --- |
| AION Nova | 71101 | http://127.0.0.1:8545 |
| AION Orbit | 71102 | http://127.0.0.1:8546 |

These are **local development chains**, not public AION networks. They reset when their containers are removed. They have no public RPC endpoint, explorer, independent validators, persistent public operation, native production asset, or deployed AION token contract.

## Start locally

Requirements: Docker with the Compose plugin and Python 3.10+.

From the repository root:

```bash
docker compose -f infra/aion-devnets/compose.yaml up -d --wait
python scripts/check_aion_devnets.py
```

Expected checks report that Nova returns chain ID 71101 and Orbit returns chain ID 71102. The script also checks that the manifest does not falsely advertise public RPCs, token deployment, or a live free-deployment promotion.

Stop and remove the temporary chains:

```bash
docker compose -f infra/aion-devnets/compose.yaml down --volumes
```

The same smoke test is configured in GitHub Actions in `.github/workflows/aion-devnets.yml`. It is an ephemeral CI test and does **not** host networks after the job ends.

## Security warnings

- The local Anvil chains use well-known development accounts and keys with test funds. Never send real assets to them, never reuse their keys, and never expose their RPC ports publicly.
- The Docker Compose port mappings are restricted to loopback (`127.0.0.1`).
- The RPC check does not deploy any contract, create a wallet, publish a token, or spend money.
- The values 71101 and 71102 are proposed/custom IDs. Check public chain registries and ecosystem tooling before any public launch.

## Gates before a real public network

1. Choose and pin an EVM client/version suitable for the intended production consensus model; Anvil is only the local test harness.
2. Create independent genesis/configuration and consensus for Nova and Orbit, with appropriate validator redundancy, keys, backups, and upgrade procedures.
3. Provision persistent RPC and validator hosting, monitoring, rate limiting, backups, TLS, incident alerts, and an on-call process.
4. Confirm a budget and ownership of all cloud resources before provisioning billable infrastructure.
5. Publish stable public RPC URLs and block explorers only after health/security verification.
6. Implement and audit the free-deployment promotion. Its scope (50 total or 50 per network), gas sponsor/relayer, abuse limits, counter, funding cap, and refund/incident policy remain undecided and disabled.
7. Audit and deploy the AION token only after the two networks have passed launch gates; verify each transaction and contract source independently.
8. Do not enable real deposits, withdrawals, bridging, custody, or exchange settlement in SI Exchange as part of this devnet work.

## Source of truth

`config/aion-networks.json` is intentionally explicit about the current non-production status. Change its production fields only alongside the corresponding deployment evidence and review.

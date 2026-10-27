# AION Online Foundation

## Goal
Make AION's public-facing services reachable online, observable, and auditable without pretending that planned components are already live. This document is the service inventory and launch gate.

## Service inventory

| Service | Current state | Public endpoint / evidence | Required before production |
|---|---|---|---|
| SI Exchange demo | Hosted demo exists; simulated assets only | https://si-exchange-1vq1.vercel.app | Persistent database, auth/roles, abuse limits, independent security review before any real-money use |
| AION source of truth | GitHub repository | https://github.com/AION-AUTONOMOUS/AION | Protected branches, reviewed changes, secrets hygiene |
| AION Nova EVM chain | Planned, not running | None yet | Client, validators/consensus, RPC, explorer, monitoring, backups, genesis/chain ID review |
| AION Orbit EVM chain | Planned, not running | None yet | Separate genesis/state, RPC, explorer, monitoring, backups, chain ID review |
| AION Coin on Nova/Orbit | Not deployed | No contract addresses or transaction hashes | Reviewed source, funded deployment account, deployment receipt and verified explorer source |
| AION Coin on BSC testnet | Deployment blocked | No confirmed contract address | Fix repository secret `DEPLOYER_PRIVATE_KEY` privately; rerun workflow and verify receipt |
| Digital vault / treasury | Design and access controls required | No public key material should be published | Separate wallets, hardware-backed key custody, multisig, offline recovery, audited procedures |
| Free first-50 deployment offer | Not live | No sponsor endpoint | Define whether 50 total or per chain; sponsor budget, anti-abuse, counters, monitoring, terms |
| Company email and customer reports | Account connection/automation must be verified | Do not infer delivery from configuration alone | Send a test message, inspect provider delivery result, monitor failures |

## Operating rules

1. **Evidence over claims.** A service is "live" only after a successful public health check and a recorded owner, endpoint, timestamp, and result.
2. **No secret in Git.** Never commit API keys, deployer private keys, seed phrases, database passwords, or webhook tokens. Do not paste them into chat.
3. **No paid infrastructure without explicit budget approval.** Public EVM chains require continuously running nodes and usually incur hosting, bandwidth, storage, monitoring, and security costs.
4. **Demo is not production.** SI Exchange's current balances, market prices, orders, and AION/SAR price are simulated. Do not describe them as live exchange trading.
5. **No free gas promise until funded.** The first-50 offer requires a gas sponsor/relayer, a hard spending cap, abuse controls, and an auditable counter.
6. **No token deployment claim without evidence.** Record chain ID, RPC, contract address, transaction hash, source commit, and verified explorer page for every deployment.
7. **Keep networks independent.** Nova and Orbit need separate genesis/state, node configuration, chain IDs, RPCs, and explorers. EVM compatibility does not inherit BNB Chain's security.

## Public service readiness monitor

The workflow `.github/workflows/aion-online-readiness.yml` checks only HTTPS URLs explicitly configured as GitHub repository variables. It reports HTTP reachability, not product correctness, security, blockchain consensus, or token deployment. Unconfigured endpoints are reported as not configured, never as healthy.

Configure repository variables (not secrets) only for public endpoints that should be checked:
- `AION_EXCHANGE_URL`
- `AION_NOVA_RPC_HEALTH_URL`
- `AION_ORBIT_RPC_HEALTH_URL`
- `AION_COIN_EXPLORER_URL`

The two chain health URLs should be added only after the respective nodes and health routes genuinely exist. A generic RPC endpoint may return JSON-RPC errors for a simple GET; preferably expose a minimal HTTPS health endpoint that confirms node synchronization and chain ID. The monitor deliberately does not send transactions.

## Launch sequence

1. Keep the exchange demo clearly labeled as simulated.
2. Fix the BSC testnet deployment secret and confirm a testnet deployment with explorer evidence.
3. Build reproducible local Nova and Orbit devnets in CI; test independent chain IDs and transaction execution.
4. Select a production EVM client/consensus design and complete a threat model.
5. Obtain explicit infrastructure budget approval; provision nodes, RPC, monitoring, backups, and explorers.
6. Deploy and verify AION Coin separately on each network only after the launch gates pass.
7. Implement and test the first-50 gas sponsor before advertising the offer.
8. Add treasury, vault, reporting, and customer systems with least-privilege access and recovery procedures.

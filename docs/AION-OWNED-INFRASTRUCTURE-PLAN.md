# AION-Owned Infrastructure and 24/7 Network Operations

Status: implementation plan; **no physical servers have been purchased or installed, and no public AION Nova/Orbit network is running yet.**

## Objective
Move AION-controlled services toward portable, self-hosted infrastructure so AION controls its configuration, keys, data, backups, deployment process, and recovery procedures. Owning a repository or cloud account does not mean owning the provider's physical machines.

## Proposed architecture (staged, no paid resources started by this document)
1. **Stage 0 — reproducible software:** pin client versions; store infrastructure-as-code, genesis files, chain configuration, monitoring, backup/restore scripts, and runbooks in version control. Keep secrets outside Git.
2. **Stage 1 — lab validation:** run each EVM chain in an isolated local/test environment. Validate genesis, chain IDs, RPC access control, block production, restart recovery, and restore from backup. Local-only tests are not public networks.
3. **Stage 2 — company-owned hardware:** purchase or lease dedicated physical servers only after an explicit budget and location decision. Install a supported Linux OS, encrypted storage, remote management, UPS, cooling, firewall, and out-of-band access. Keep hardware inventory and warranty details in the company vault.
4. **Stage 3 — resilient production:** each chain needs independently operated validators/sealers appropriate to its consensus protocol, bootnodes, private peer networking, public RPC gateways, monitoring/alerts, and geographically separated recovery capacity. A single server is a single point of failure and must not be described as highly available.
5. **Stage 4 — controlled public release:** independent security review, chain-ID collision check, genesis/config freeze, reproducible deployment, public explorer and faucet, abuse controls, incident response, and documented recovery drill before announcing availability.

## Availability and disaster recovery
- Target only after the hardware topology is funded and tested: 24/7 monitoring; automated alerts; defined RPO/RTO; tested restoration; documented operator escalation.
- Keep at least three copies of critical data across two storage types, with one encrypted offline or separately controlled copy. Do not put private keys, seed phrases, API tokens, or unencrypted wallet files in Git or ordinary backups.
- Back up chain configuration/genesis, deployment manifests, service configuration without secrets, validator metadata, application databases, and release artifacts. For chain data, use client-supported snapshots or documented consistent snapshots; test restoration regularly.
- Monitor disk capacity, peer count, block height/production, RPC latency/errors, CPU/RAM, temperature, SMART/RAID, backup freshness, certificate expiry, and security updates.
- Document key rotation, compromised-validator response, DDoS response, restore steps, and how to safely halt a chain.

## Free first-50 deployment offer
Gas is not inherently free. A capped offer needs an explicitly funded gas sponsor/relayer or a protocol-level subsidization mechanism, per-network accounting, anti-abuse/rate limits, budget ceilings, and a kill switch. Define whether the 50 free deployments are total across both chains or 50 per chain before implementation. Never promise unlimited free usage.

## Security and custody rules
- Never request or commit a user's wallet recovery phrase or private key.
- Separate deployer, validator, treasury, and operations keys; use hardware-backed or offline key storage where practical.
- Require explicit approval for mainnet token deployment, treasury transfers, paid infrastructure, or other irreversible/high-cost actions.
- Do not enable real deposits, withdrawals, bridges, or live trading until audits and operational readiness gates pass.

## Decisions required before buying/launching
1. Approved one-time hardware budget and recurring power/network/colocation budget.
2. Whether equipment will be held at an AION-controlled site or in a colocation facility (colocation is not physical ownership of the building/network).
3. Country/jurisdiction, power, cooling, bandwidth, static IPs, DDoS mitigation, and physical access arrangements.
4. Consensus model and number of independent validators/operators for each chain.
5. Whether the first-50 offer is 50 deployments total or 50 per network.

## Acceptance checklist
- [ ] Hardware inventory, ownership/purchase evidence, and out-of-band access documented.
- [ ] Two distinct chain IDs checked for collision and genesis files reviewed.
- [ ] At least one isolated test deployment per chain passes automated tests.
- [ ] Production topology avoids a single validator/server failure mode.
- [ ] Monitoring and alert delivery tested at all hours.
- [ ] Encrypted off-site/offline backups and restore drill pass.
- [ ] Security review and incident/recovery runbooks approved.
- [ ] Public endpoints and explorer are reachable from an external network.
- [ ] AION token contract addresses and transaction hashes independently verified before any claim of deployment.

**Current factual status:** this document is a plan. It does not provision hardware, buy equipment, start a public chain, or deploy a token.

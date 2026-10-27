# AION Online Infrastructure and Ownership Blueprint

**Status:** implementation blueprint; this document does not itself provision cloud resources, register domains, create legal ownership, or launch blockchain networks.

## Objective
Keep AION's source code, deployment process, product data, digital assets, and operational evidence under company-controlled accounts wherever possible. Third-party hosting, DNS, identity, and cloud services remain external dependencies even when AION owns the account and pays the bill.

## Ownership and control model
- Use company-controlled GitHub organization/repositories as the source of truth; require MFA, least privilege, protected main branches, reviewed changes, and audited Actions.
- Use a company-controlled domain registrar and DNS account. Register domains only after the owner, renewal cost, and recovery contact are confirmed.
- Use separate production and test environments. Keep production secrets in the hosting provider's secret manager and GitHub Actions environment secrets; never store credentials in source code, logs, issues, or chat.
- Keep at least two authorized administrators with MFA and documented account recovery. Do not make a single AI agent the sole owner or recovery path.
- Maintain an asset register recording account owner, service, URL, purpose, data class, recovery method, cost ceiling, backup method, and evidence of operation.

## Service map
1. **Public web / product catalogue:** SI Exchange and AION product pages. Use HTTPS, security headers, accessibility and Arabic RTL checks, uptime monitoring, and an incident contact.
2. **Application API:** authenticated endpoints, input validation, rate limits, structured redacted logs, health checks, and documented API contracts.
3. **Data store:** managed database only after schema, access roles, retention, backup, and restore testing are defined. Never treat a demo/in-memory ledger as a production financial ledger.
4. **Digital vault:** encrypted secret and document storage, least-privilege access, key rotation, audit trail, and tested recovery. A website or Git repository is not a safe place for seed phrases or private keys.
5. **AION Coin / treasury:** distinguish token source code, testnet deployments, verified on-chain contracts, treasury wallets, and accounting records. Use multisig for treasury/admin actions where practical. Never publish seed phrases or private keys.
6. **Nova and Orbit networks:** independent EVM client, genesis, validators/consensus, RPC nodes, explorers, faucet/sponsored gas, metrics, backups, and incident procedures for each network. Do not call a local test or single unmonitored node a public production chain.
7. **CI/CD:** automated unit/integration/security checks; staging first; production releases gated by explicit approvals; deployment records include commit, environment, run ID, and rollback plan.
8. **Monitoring and backup:** health/latency/error alerts, log retention, encrypted backups, documented RPO/RTO targets, and periodic restore drills.
9. **Company communications:** company-controlled email and a second recovery channel. Avoid relying on one mailbox for all authentication and recovery.
10. **Evidence layer:** maintain a timestamped register of live URLs, HTTP/health checks, deployment IDs, chain IDs, contract addresses and transaction hashes, backup test results, and open blockers.

## Required security boundaries
- No private keys, seed phrases, API tokens, passwords, or recovery codes in chat, commits, issue bodies, screenshots, or logs.
- Use test credentials and test funds for initial verification. Do not enable real deposits, withdrawals, custody, bridges, or live trading without separate legal, security, and operational review.
- No paid cloud provisioning, domain purchases, paid APIs, or other spend without a defined budget and explicit approval.
- Do not claim that a service is live, owned, backed up, secure, or revenue-generating without verifiable evidence.
- A hosted service is not wholly owned infrastructure: AION can own its accounts, code, domain registration, and data while remaining dependent on cloud vendors and their terms.

## Implementation sequence
### Phase 1 — Inventory and baseline
- Inventory all existing repositories, production URLs, domains, hosting projects, payment integrations, wallets, workflows, and service accounts.
- Classify each item as **verified live**, **configured but unverified**, **planned**, or **blocked**.
- Record the accountable owner, recovery method, recurring cost, and evidence link for each item.

### Phase 2 — Secure the foundation
- Enforce MFA and least privilege; remove stale tokens; rotate exposed credentials.
- Add environment separation, secret scanning, dependency checks, branch protection, and deploy approvals.
- Define data retention, privacy, incident response, backups, and restore testing.

### Phase 3 — Online products
- Keep the SI Exchange demo clearly labelled as simulation until a reviewed production backend, database, identity controls, and audit ledger exist.
- Deploy public product pages and APIs with HTTPS, monitoring, and documented ownership.
- Add a company-controlled document vault only after encryption, access controls, backups, and recovery are tested.

### Phase 4 — Blockchain infrastructure
- Build reproducible local devnets and CI tests first; then stage Nova and Orbit separately.
- Validate unique chain IDs, genesis, consensus, RPC security, node persistence, explorer indexing, monitoring, and recovery.
- Implement and audit the capped first-50 free-deployment sponsorship before advertising it.
- Deploy AION Coin only after contract review and network readiness. Record independently verifiable explorer links, contract addresses, transaction hashes, and source verification.

### Phase 5 — Operational acceptance
A component is **live** only when its public endpoint responds as expected, deployment identity is recorded, security checks pass, monitoring is active, and rollback/recovery is documented. Blockchain deployment additionally requires an independently verifiable chain and transaction record.

## Current known blockers carried forward
- AION Coin BNB Smart Chain testnet workflow previously failed because the GitHub Actions `DEPLOYER_PRIVATE_KEY` secret was malformed. Replace it privately with a valid 32-byte hexadecimal private key only if the deployer wallet is intended and funded for testnet; never share it in chat.
- AION Nova and AION Orbit are proposed networks until actual clients/nodes, consensus, RPCs, explorers, monitoring, and on-chain evidence exist.
- The SI Exchange demo must not be represented as a live exchange or real-money service.

## Evidence register template
| Component | Status | Public URL / resource | Owner account | Cost ceiling approved? | Last evidence | Blocker |
|---|---|---|---|---|---|---|
| SI Exchange | Fill after live check | https://si-exchange-1vq1.vercel.app | Confirm | No spend without approval | Production deployment ID recorded in project notes | Production backend/security status to verify |
| AION main repository | Repository exists | https://github.com/AION-AUTONOMOUS/AION | Confirm organization access | N/A | GitHub repository | Testnet deployer secret blocker |
| Nova | Planned | Not available | AION-controlled account to establish | No | None | Network not provisioned |
| Orbit | Planned | Not available | AION-controlled account to establish | No | None | Network not provisioned |
| Digital vault | Planned / inventory required | Not available | AION-controlled account to establish | No | None | Choose and secure storage design |
| AION token on Nova/Orbit | Not deployed | No contract address | AION treasury/deployer governance required | No | None | Network and contract readiness gates |


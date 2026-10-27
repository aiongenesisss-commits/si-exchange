# AION-owned digital infrastructure roadmap

**Purpose:** build an internet-accessible AION-operated platform for AION AUTONOMOUS, the AION token, AION Vault, and SI Exchange. This document is a roadmap, not a claim that every service is already running or owned.

## Service portfolio

| Internal product name | Responsibility | Minimum ownership evidence |
| --- | --- | --- |
| AION Nova | Proposed EVM network, chain ID 71101 | Published genesis/config hash, independently reachable RPC, peer/validator telemetry, explorer, runbook |
| AION Orbit | Proposed independent EVM network, chain ID 71102 | Separate genesis/config hash, RPC, peer/validator telemetry, explorer, runbook |
| AION Coin | ERC-20-compatible token deployment per approved chain | Verified source, chain ID, contract address, deployment transaction, tests, supply/authority disclosure |
| AION Vault | Wallet/key-management interface and treasury controls | Threat model, audit, secure signing design, role separation, recovery plan; never store plaintext private keys |
| AION RPC | Managed JSON-RPC gateway | Authentication/rate limits where applicable, quotas, metrics, abuse controls, uptime alerts |
| AION Explorer | Blocks, transactions, tokens, verified contracts | Indexed chain data, source verification, status/backup plan |
| AION Faucet | Test tokens only | Rate limits, anti-abuse policy, per-wallet quotas, explicit testnet-only labeling |
| AION Developer Portal | Chain configuration, SDKs, docs, status | Versioned chain metadata, tested examples, API status and incident notices |
| AION Monitor | Uptime, RPC latency, validator health, alerts | External probes, alert routing, retention and incident ownership |
| AION Identity | Authentication and organization access | Least privilege, MFA, audit logs, account recovery process |
| AION Mail | Company-domain email and notifications | Domain control, SPF/DKIM/DMARC, deliverability monitoring, provider ownership/contract clarity |
| SI Exchange | Arabic RTL trading simulation and developer demo | CI tests, accessible HTTPS deployment, clear simulated-funds disclosure, audited backend before real trading |

## Ownership principles

1. Use AION-controlled source repositories, domains, deployment accounts, billing identities, access policies, and backups.
2. Rebrand the user-facing service where useful, but do not describe a third-party provider as owned by AION merely because it has an AION label.
3. Open-source software may be self-hosted subject to its license. Keep license notices and security updates.
4. Prefer portable containers and documented configuration to avoid lock-in. Keep secrets in managed secret storage, never source control.
5. Track every dependency and vendor in an internal register, with cost, data handling, exit plan, and owner.
6. Maintain separate development, testnet, and production environments. Use least privilege and multi-person review for irreversible financial actions.

## Launch gates

### Gate 0 — Repository and local repeatability
- Compose-based Nova and Orbit development chains run locally on loopback only.
- CI verifies distinct chain IDs and basic RPC responses.
- Contract deployment tests use only throwaway test accounts.

### Gate 1 — Public testnet
- Chain IDs and genesis finalized and collision-checked.
- Independent nodes/validators, peer discovery, persistent storage, monitoring, backups, RPC protections, and incident runbooks in place.
- External security review completed; testnet is clearly labeled non-production.
- Hosting budget explicitly approved.

### Gate 2 — Token testnet deployment
- Token source and tokenomics reviewed; minting/admin roles documented.
- Unit/integration tests and independent verification complete.
- Deployer key is generated and stored in protected secret management; never pasted into chat or committed.
- Deployment transaction and verified contract address published only after chain explorer confirms them.

### Gate 3 — Sponsored first 50 deployments
- Product owner decides 50 total or 50 per network.
- Sponsor wallet is funded and bounded by a hard spending cap.
- On-chain or backend audit log prevents duplicate/abusive claims and reports remaining quota.
- Public terms state what is free, eligibility, expiry, and what fees are not covered.

### Gate 4 — Production financial services
- Independent security audit, legal/compliance review, custody design, operational controls, incident response, and user disclosures complete.
- No real deposits, withdrawals, custody, bridging, or live trading before all relevant gates are signed off.

## Current known blockers

- Nova and Orbit are proposed; the local Compose stack is only a development harness.
- Chain IDs 71101/71102 are proposals, not confirmed globally unique.
- No public node/validator fleet, production RPC, explorer, or faucet is established by this roadmap alone.
- AION Coin has no verified deployed address on these proposed networks.
- A previous BNB Smart Chain testnet attempt failed validation because the GitHub Actions deployer-key secret was malformed. Replace it privately in repository Actions secrets; do not share it in chat.
- SI Exchange production URL is a simulation/demo, not a live exchange or custody system.
- Paid hosting and external services require a defined budget and explicit approval.

## Operating rule

Every status report must separate **planned**, **implemented in source**, **deployed**, and **independently verified**. Never count simulated balances, unverified deployments, or planned services as live assets or revenue.

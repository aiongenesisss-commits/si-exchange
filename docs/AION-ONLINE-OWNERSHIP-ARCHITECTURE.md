# AION Online Ownership & Operations Architecture

**Status:** architecture and implementation gates; not a claim that all services are provisioned or owned yet.

## Goal

Operate AION AUTONOMOUS, AION Coin, the AION digital vault, and SI Exchange through an online-first control plane with verifiable ownership, secure access, durable records, and clear service health. Keep components replaceable and exportable so AION can migrate providers without losing source, data, keys, or domain control.

## Current verified baseline

- SI Exchange source repository: `aiongenesisss-commits/si-exchange`.
- The repository describes an Arabic RTL exchange demo with simulated balances, orders, matching, and ledger. It explicitly has no live trading, deposits, withdrawals, custody, payment processing, or blockchain connection.
- The AION two-network initiative is a plan only: AION Nova (proposed chain ID 71101) and AION Orbit (proposed chain ID 71102) are not publicly running.
- AION Coin's BNB Smart Chain testnet deployment is blocked until the repository secret `DEPLOYER_PRIVATE_KEY` is privately corrected. No contract address or transaction hash has been verified.
- These baselines must be rechecked before any public status page or investor-facing statement is updated.

## Service map and ownership evidence

| Capability | Required online component | Evidence required before marking live |
|---|---|---|
| Source and change control | GitHub organization/repositories, protected default branch, reviewed PRs | Repository URL, permissions review, branch protection and recent CI run |
| Public web and API | HTTPS application hosting, custom domain, TLS | Public URL, successful health check, TLS validation, deployment commit |
| SI Exchange | Web app/API plus durable database and migrations | Production smoke tests, database persistence test, audit endpoint, backup/restore evidence |
| AION Coin | Reviewed Solidity source, reproducible deployment workflow | Chain ID, RPC, explorer URL, verified contract address and transaction hash |
| AION Nova | EVM client, genesis, validator/bootnode, RPC, monitoring | Independent node sync/consensus test, public RPC health, documented recovery |
| AION Orbit | Separate EVM deployment with independent configuration | Same evidence as Nova; no shared mutable chain data or accidental chain-ID reuse |
| Digital vault | Encrypted secret manager plus encrypted document/object storage | Access policy, recovery drill, audit log; never store plaintext private keys in app DB |
| Wallet operations | Hardware-backed or dedicated signing key, multisig for critical treasury actions | Key custody policy, signer separation, recovery procedure, test transaction |
| Payments/revenue | Payment provider, signed webhooks, idempotent order processing | Verified webhook signature, successful test event, reconciled order ledger |
| Email and reporting | Company mailbox, authenticated sending domain, scheduled report job | Verified sender/domain, delivery test, failure alert and report history |
| Search/indexing | Sitemap, robots policy, Search Console/Bing tools, IndexNow where supported | Submitted URL and provider confirmation; submission is not a ranking guarantee |
| Monitoring and response | Uptime probes, application logs, alert routing, incident runbook | Alert test, on-call owner, restore and incident exercise |
| Backups and portability | Automated encrypted backups and documented exports | Restore test with measured recovery time; no vendor-only copy of critical data |

## Online-first deployment sequence

### Stage 0 — establish control and inventory

1. Confirm which GitHub organization, hosting projects, domains, cloud accounts, email, payment account, and wallet addresses are legally/administratively controlled by AION.
2. Enable MFA/passkeys, least-privilege access, branch protection, environment approvals, and audit logging.
3. Record each service owner, billing owner, renewal date, data location, backup/export method, and recovery contact.
4. Keep an evidence register with timestamp, source URL, deployment commit, health result, and status: `planned`, `configured`, `verified`, or `blocked`.

### Stage 1 — reliable public web platform

1. Deploy SI Exchange only as a clearly labeled simulation until financial, custody, and legal reviews are complete.
2. Attach a domain controlled by AION and verify HTTPS/TLS.
3. Use managed PostgreSQL only after explicit budget approval; otherwise keep the demo explicitly non-durable and do not call it production.
4. Configure health checks, logs, alerts, database backups, migration checks, and restore drills.
5. Publish a truthful status page distinguishing demo, testnet, and production.

### Stage 2 — digital vault and treasury controls

1. Use a dedicated secret manager for API credentials and CI secrets; never commit secrets or send them in chat.
2. Keep wallet private keys outside the web app and database. Never request seed phrases or recovery phrases from users.
3. Use a dedicated test wallet for testnets and multisig / separated approval for any treasury mainnet action.
4. Require explicit approval before any paid infrastructure, on-chain mainnet deployment, token transfer, bridge, or real-money feature.
5. Back up business documents with encryption and test restoration.

### Stage 3 — AION networks

1. Build repeatable local/devnet configurations and automated tests before public infrastructure.
2. Select an actively maintained EVM client and document the exact version, genesis, consensus, validator count, ports, resource sizing, and upgrade path.
3. Run Nova and Orbit as separate networks with unique chain IDs, genesis hashes, RPC endpoints, keys, data volumes, monitoring, and recovery plans.
4. Protect public RPC with rate limits, method allowlists, abuse monitoring, and no exposed admin/debug APIs.
5. Implement the first-50-free-deployment offer only after defining whether it means 50 total or 50 per network and funding an abuse-limited gas sponsor. EVM gas is not inherently free.
6. Do not deploy AION Coin to either network until chain health and token source review pass. Verify source and record addresses and transaction hashes.

### Stage 4 — payment and customer workflow

1. Treat an order as paid only after a valid signed provider webhook or provider-side confirmation is verified server-side.
2. Make webhook processing idempotent and reconcile provider events against the order ledger.
3. Do not collect card details or custody funds in the application.
4. Publish clear terms, privacy policy, support contact, refund policy, and accurate product descriptions before accepting customer payments.

### Stage 5 — operating governance

- Daily automated report: uptime, failed jobs, latest deployment commit, test status, backups, payment reconciliation, incidents, and blocked approvals.
- Weekly restore/security review and monthly access/billing review.
- Each claim of launch, revenue, users, token deployment, or network readiness must link to evidence.
- Keep a provider-independent export of source, configuration, database, documents, and operational runbooks.

## Budget and approval policy

No paid hosting, domains, databases, monitoring tiers, transaction fees, ads, or third-party subscriptions may be initiated without an explicit approved budget. Free tiers have limits and are not a guarantee of production reliability. If a free tier cannot meet reliability or security requirements, mark the component **blocked pending budget approval** rather than silently enabling paid resources.

## Go-live definition

A component is **live** only when its public URL or endpoint is reachable over valid HTTPS (where applicable), its deployed commit/version is known, automated health and security checks pass, persistence and backup/restore are proven where required, an owner and recovery path are documented, and there is no unresolved critical issue.

A token is **deployed** only when a confirmed chain ID, contract address, transaction hash, and explorer record exist. A chain is **public** only when independent nodes can reach consensus and the public RPC is monitored. A plan, workflow file, green build, or dashboard mock-up is not proof of a live chain or token.

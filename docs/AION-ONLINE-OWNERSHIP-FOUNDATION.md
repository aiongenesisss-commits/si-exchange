# AION Online Ownership & Operations Foundation

**Status date:** 2026-10-27  
**Purpose:** Make AION's software, SI Exchange, digital-asset tooling, and operational records internet-accessible while keeping ownership, keys, and spending under explicit control.

## 1. Verified starting point

- SI Exchange repository: https://github.com/aiongenesisss-commits/si-exchange
- SI Exchange production web app: https://si-exchange-1vq1.vercel.app
- SI Exchange is a demo exchange. Market prices and balances are simulated; it is not a live exchange, custodian, or payment processor.
- AION main repository: https://github.com/AION-AUTONOMOUS/AION
- AION Coin has **no verified deployed contract address or transaction hash** in the current evidence. The BNB Smart Chain testnet workflow failed because the `DEPLOYER_PRIVATE_KEY` GitHub Actions secret was malformed. Do not claim a deployment until an explorer verifies it.
- AION Nova (proposed chain ID 71101) and AION Orbit (proposed chain ID 71102) are proposals, not running public networks.
- A public EVM network and a gas-free first-50 deployment offer require actual nodes/consensus, monitoring, a funded sponsor, abuse controls, and operating costs. Never describe a local test as a public network.

## 2. Ownership model

AION should retain control of its source code, domains, deployment accounts, DNS, application configuration, secrets, backups, and release approvals. Hosting vendors provide infrastructure; using a vendor does not mean AION owns the vendor or its physical hardware.

For each external service, maintain a private inventory with:
- service and purpose;
- legal/account owner and recovery contact;
- repository/project and production URL;
- billing status and spending limit;
- deployment environment and rollback procedure;
- data classification, backup method, and restore test;
- key rotation and incident contact.

Do not put private keys, seed phrases, API secrets, recovery codes, or sensitive customer data in this repository or issue tracker.

## 3. Target online architecture

1. **Public web:** SI Exchange and AION company/product pages served over HTTPS.
2. **API layer:** versioned endpoints, health/readiness probes, strict input validation, authentication for administrative routes, rate limits, and structured redacted logs.
3. **Identity and access:** individual accounts, least privilege, MFA, separate production and test credentials, and audited administrative actions.
4. **Digital Vault:** encrypted storage for business documents and non-secret records. Signing keys must remain in a dedicated key-management solution or offline hardware wallet; never expose seed phrases to the web application.
5. **Treasury ledger:** append-only, reconciled records; no withdrawal without explicit authorization and independent verification.
6. **AION Coin:** reproducible contract build, reviewed tokenomics, tests, testnet deployment, explorer verification, and independent security review before mainnet.
7. **Nova and Orbit:** separate chain configurations, chain-ID collision checks, client/consensus selection, validator and RPC security, persistent nodes, monitoring, explorer/faucet, backup and disaster recovery.
8. **Operations:** CI tests, deployment approvals, health alerts, dependency scanning, documented rollback, and evidence-based status reporting.

## 4. Release gates (must not be bypassed)

### Gate A — Web application
- CI tests pass on the exact release commit.
- HTTPS works; health and readiness endpoints pass.
- No secrets are bundled into client-side assets.
- Admin endpoints require authentication and rate limiting.
- Backup and rollback have been tested.
- The production URL is checked after deployment.

### Gate B — Vault and wallet
- No seed phrase/private key is ever requested in chat, logged, or committed.
- Encrypted backups and a restore test exist.
- Access is least-privilege and audited.
- A custodial wallet service is not implied by a UI-only wallet screen.

### Gate C — AION Coin
- Secret `DEPLOYER_PRIVATE_KEY` is supplied privately in GitHub Actions secrets as a valid 32-byte hex private key (64 hex characters, optional `0x` prefix), never as a wallet address.
- Run contract tests and a testnet deployment.
- Verify the contract address and transaction on the chain explorer.
- Review ownership/admin controls, supply, mint/burn behavior, and recovery.
- Mainnet deployment requires a separate explicit approval and a final preflight; no automated workflow may silently spend funds or deploy to mainnet.

### Gate D — Nova and Orbit public networks
- Verify chain IDs are unique and document genesis parameters.
- Run reproducible multi-node testnets with independent validators and restart/recovery tests.
- Secure public RPC endpoints, rate-limit abusive traffic, and monitor node health.
- Test chain reorganization/finality assumptions, backups, upgrades, and incident response.
- Publish RPC/explorer only after tests and operational readiness are evidenced.
- Fund and cap the “first 50 free deployments” sponsor; specify whether the cap is total or per chain and prevent double claims/Sybil abuse.

## 5. No-spend and security policy

- No paid infrastructure, domain purchase, advertising, or transaction spending without explicit budget approval.
- Prefer free tiers for demos, but do not represent a free-tier single node as production-grade blockchain infrastructure.
- Never ask the owner to send a private key or recovery phrase in chat.
- Use separate test and production accounts/secrets.
- Public status reports must distinguish **implemented**, **tested**, **deployed**, and **verified on-chain**.

## 6. Immediate execution order

1. Keep SI Exchange online as a clearly labelled simulation while hardening its API and release checks.
2. Fix the malformed BSC testnet deployment secret privately in GitHub; rerun testnet deployment; capture explorer-verified address and transaction.
3. Build and test a non-custodial wallet interface only after defining the threat model; never hold user keys on the server.
4. Deploy a private encrypted document vault and prove backup restoration before storing sensitive company records.
5. Establish reproducible local/multi-node devnets for Nova and Orbit before any public RPC launch.
6. Publish only verified endpoints, contract addresses, chain IDs, and operating status.

## 7. Evidence log template

For every release or network milestone, record:
- timestamp (UTC);
- repository, branch, and exact commit SHA;
- CI workflow URL and result;
- deployment URL and provider deployment ID;
- health/readiness result;
- explorer URL and transaction hash, when applicable;
- operator, approval reference, and rollback result.

**Current status:** this document is an operating foundation, not proof that every listed component is already built or online. The production SI Exchange demo is online; a live exchange, custodial vault, deployed AION Coin, and public Nova/Orbit networks are not verified by the evidence above.

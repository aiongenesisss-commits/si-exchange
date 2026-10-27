# AION / SI Exchange — Ownership & Control Register

Last reviewed: 2026-10-27  
Purpose: distinguish assets AION controls from third-party infrastructure and proposals. This register is evidence-led; a repository entry or URL alone does not prove legal title, exclusivity, or production readiness.

## 1. Source code and repositories

| Asset | Current evidence | Control / ownership statement | Status |
|---|---|---|---|
| AION core repository | https://github.com/AION-AUTONOMOUS/AION | Source repository is under the AION-AUTONOMOUS GitHub organization. Legal IP title and organization billing/admin access must be verified in GitHub settings and company records. | Repository exists; individual systems have different readiness levels. |
| SI Exchange demo | https://github.com/aiongenesisss-commits/si-exchange | Source repository is under the aiongenesisss-commits GitHub account. Treat code as controlled through that account; legal assignment to AION requires an explicit record. | Arabic RTL demo; simulated markets only. |
| AION two-network plan | https://github.com/aiongenesisss-commits/si-exchange/blob/main/docs/AION-TWO-NETWORKS-PLAN.md | Planning document in SI Exchange repository. | Proposal only; Nova and Orbit are not public/running. |

## 2. Deployment and hosting

| Service | Verified reference | What AION controls | Limitation / action |
|---|---|---|---|
| Vercel SI Exchange (intended app) | https://si-exchange-1vq1.vercel.app | Deployment is hosted by Vercel; AION's control depends on team and project permissions. | This is third-party hosting, not infrastructure owned outright by AION. Verify current READY status before calling it production. |
| Vercel project named `si-exchange` linked to AION core repo | Team project ID `prj_jNMM9WesDaJPpNA03mHyvfQ8CaQw` | This project was mislinked to `AION-AUTONOMOUS/AION` while configured for FastAPI and generated repeated `FASTAPI_ENTRYPOINT_NOT_FOUND` errors. | Project paused on 2026-10-27 to stop the broken auto-deployment loop. Reconnect only after selecting the correct repository/root/framework. Existing failure emails are historical and may continue arriving. |
| Vercel SI Exchange duplicate project | Project `si-exchange-1vq1`, linked to `aiongenesisss-commits/si-exchange` | Third-party deployment under the Vercel team. | Keep this as the intended SI Exchange deployment unless a verified replacement is chosen. |
| Railway / other cloud | Account and billing evidence not included here | No claim of ownership of the cloud provider or its physical infrastructure. | Record project IDs, billing owner, domains, environment variables and service status only after checking the relevant provider dashboard. |

## 3. AION Coin and digital assets

- Planned AION token source: `AIONCoinV2`; planned supply: 10,000,000,000; BNB Smart Chain testnet chain ID: 97.
- The latest known testnet workflow failed because the GitHub Actions secret `DEPLOYER_PRIVATE_KEY` was malformed. No verified contract address or transaction hash is recorded here.
- No verified AION token deployment on AION Nova or AION Orbit. The proposed chain IDs 71101 and 71102 are not proof of live networks.
- Wallet addresses are identifiers, not proof of ownership. Keep a separate confidential custody register showing wallet label, network, public address, custodian, creation method, access approvers and last verification. Never record seed phrases or private keys in this file, GitHub issues, email or chat.

## 4. Domains, accounts, data and credentials

For each account or asset, record: service/provider, account owner, legal entity, admin/recovery contacts, MFA status, billing owner, connected repositories, domain/DNS control, data export/backup method, renewal date, and offboarding/recovery procedure. Store secrets only in the provider's secret manager; do not commit credentials.

## 5. Evidence rules

1. Mark an asset **owned/controlled** only when there is evidence of the legal owner and authorized administrative access.
2. Mark a deployment **live** only after a successful deployment and an external health check.
3. Mark a token **deployed** only after a chain ID, verified contract address and transaction hash are recorded and independently checked in the appropriate explorer.
4. Mark revenue only after confirmed provider/webhook settlement; demo balances, simulated orders, and displayed prices are not revenue.
5. Keep AION source code, third-party hosting, domains, customer data, treasury assets, and proposed networks as separate register entries.
6. Never put private keys, seed phrases, API tokens, passwords, or recovery codes in this register.

## 6. Immediate actions

- [x] Document the distinction between AION-controlled source and third-party hosting.
- [x] Pause the Vercel project that was linked to the wrong repository and repeatedly failed FastAPI detection.
- [ ] Verify legal IP assignment for both repositories.
- [ ] Verify Vercel project permissions, intended production URL, and health endpoint.
- [ ] Correct the BSC testnet deployer secret privately and rerun the testnet workflow.
- [ ] Build and independently verify AION Nova and AION Orbit before describing either as online.

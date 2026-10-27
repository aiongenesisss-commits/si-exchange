# AION Two-Network Initiative — Launch Plan

Status: specification only. Neither network is running publicly and no AION token contract has been deployed to either network.

## Proposed names

1. **AION Nova** — EVM-compatible development / application network.
   - Proposed chain ID: 71101 (private/custom-chain ID; verify uniqueness before public launch).
   - Purpose: application and contract testing.
2. **AION Orbit** — EVM-compatible settlement / staging network.
   - Proposed chain ID: 71102 (private/custom-chain ID; verify uniqueness before public launch).
   - Purpose: staging and later production evaluation.

These are AION-owned proposed networks, not BNB Smart Chain and not affiliated with BNB Chain. EVM compatibility does not make them as secure, decentralized, or reliable as BNB Smart Chain.

## Free first 50 contract deployments

The policy can be implemented as a launch promotion for the first 50 successful contract deployments per network (or 50 total; product owner must define the counting rule before launch). Users must not be charged a platform deployment fee during the promotion.

Important: EVM networks normally charge gas in their native asset. To make deployment genuinely free to users, the network needs a funded gas sponsor / relayer or a protocol-level gas subsidy. The sponsor needs abuse protection, per-address limits, an auditable counter, and a hard budget. Do not advertise this as live until the sponsor and limits are implemented and tested.

## AION token deployment gates

- Deploy the same reviewed AION token source to Nova and Orbit only after both RPC endpoints, chain IDs, consensus/validator configuration, block explorers, faucet/gas sponsor, and chain health monitoring are running.
- Use a dedicated deployer wallet created for these networks; never reuse or publish a seed phrase/private key.
- Keep deployment keys in GitHub Actions secrets; never commit them or paste them into chat.
- Verify bytecode/source, token name/symbol/decimals/supply, ownership/admin controls, and deployment transaction on each explorer.
- Record each chain ID, RPC URL, explorer URL, contract address, transaction hash, source commit, and verification result.
- No real-money trading, bridging, deposits, or claims of production security until independent security review and operational readiness are complete.

## Immediate blocker

The existing BNB Smart Chain testnet deployment currently fails because the repository's `DEPLOYER_PRIVATE_KEY` secret is not valid 32-byte hexadecimal. This does not deploy AION to BNB testnet or to either proposed AION network. Correct the secret privately in GitHub Actions; do not share it in chat.

## Launch checklist

- [ ] Select and implement a supported EVM client / chain framework.
- [ ] Provision at least the required validator / RPC nodes and persistent hosting for each network.
- [ ] Configure independent genesis files, unique chain IDs, consensus, RPC allowlists/rate limits, and monitoring.
- [ ] Publish network metadata and install instructions.
- [ ] Operate faucet and funded gas sponsorship with a capped free-deployment counter.
- [ ] Run independent chain and contract tests.
- [ ] Deploy and verify AION token on Nova; record evidence.
- [ ] Deploy and verify AION token on Orbit; record evidence.
- [ ] Publish only verified addresses and clearly distinguish test assets from any production token.

Until all gates are evidenced, status remains **proposed / not deployed**.

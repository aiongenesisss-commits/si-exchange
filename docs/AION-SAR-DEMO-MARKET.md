# AION/SAR demo market integration

## Status and boundaries

AION/SAR is added to SI Exchange as a **simulated market only**. The reference value of 0.10 SAR per AION and the demo balance of 100,000 AION per demo account are deterministic test fixtures, not a market quote, valuation, offer, or representation of a deployed token. The app deliberately does not request a live AION price from a third-party exchange.

The AION project status record in the AION repository states that AION Coin remains under development and that no mainnet contract address, exchange listing, liquidity, or real price is claimed. A symbol in this demo must not be interpreted as a live asset or as evidence of a blockchain deployment.

## Included

- AION/SAR in the market list and limit-order model.
- Demo-only AION balances in both in-memory and optional PostgreSQL stores.
- Automated tests for simulated AION order matching, balance changes, ledger entries, and conservation audit.
- Explicit no-live-market source metadata for the AION reference value.

## Requirements before any real AION market

1. Verify a successful testnet deployment using the authoritative AION repository's workflow logs and a testnet block explorer. Record chain ID, contract address, transaction hash, total supply, and verified bytecode.
2. Verify the intended token contract and network independently; do not infer mainnet from BNB Smart Chain testnet (chain ID 97).
3. Complete security review, token allocation/treasury checks, and applicable legal/compliance review.
4. Build a separate production-market integration with real custody, settlement, market data, monitoring, and operational controls. This demo is not a production exchange.
5. Do not enable mainnet deployment, wallet signing, real deposits/withdrawals, or movement of real funds from this change.

## Current validation

The change is intended for review and CI validation. It does not deploy AION Coin, create liquidity, connect a wallet, or enable live trading.

# AION Portable Platform — Delivery Plan

## Objective

Build an AION-owned, reproducible platform that can be tested on a developer machine, exported as a verifiable offline bundle, installed on a compatible Linux host without contacting package registries, and eventually run on AION-controlled infrastructure. The SI Exchange remains a simulation until each gate has evidence.

## Stage 1 — Reproducible application bundle

**Current baseline:** Debian-based container build, automated application tests, health-route verification, image export/reload and SHA-256 manifest are implemented in the Linux Container Verification workflow. A real disconnected target-host installation has not yet been demonstrated.

Acceptance gates:
- [ ] All CI checks pass on one exact commit.
- [ ] Bundle contains the exact tested image, source, install/verify/rollback scripts, SBOM or dependency inventory, license notices, and checksums.
- [ ] A clean compatible Linux host with Docker installed can import and start the bundle with outbound network access disabled.
- [ ] A documented smoke test verifies health, dashboard, API, and simulated order lifecycle.
- [ ] A backup/restore rehearsal verifies data recovery.
- [ ] Build provenance records commit, tool versions, image digest, and artifact SHA-256.

## Stage 2 — Durable simulation database

The existing PostgreSQL schema is only a foundation. Do not describe persistence as operational until the app uses it.

Implementation sequence:
1. Add a repository abstraction with the current in-memory engine retained as the default test adapter.
2. Add an explicit opt-in PostgreSQL adapter configured only by `DATABASE_URL`; fail closed on startup if explicitly enabled but unavailable. Never silently fall back from configured persistence to volatile memory.
3. Move demo account seeding, balances, orders, fills, idempotency keys, and audit events into database transactions.
4. Use fixed-precision decimal arithmetic for price, quantity, and value. Avoid binary floating-point for ledger calculations.
5. Serialize order-book mutations with appropriate row/advisory locks; enforce balance reservations and matching inside one transaction.
6. Make idempotency key + request fingerprint + order creation atomic; same key/same payload returns the original order, same key/different payload returns HTTP 409.
7. Add PostgreSQL integration tests for restart persistence, concurrency, partial fills, rollback, duplicate requests, audit reconciliation, and asset conservation.
8. Add migration version tracking, least-privilege runtime role, separate migration role, backup/restore scripts, and data-retention rules.
9. Keep all funds simulated and reject any real-money, custody, deposit, withdrawal, or live-trading mode.

Acceptance gates:
- [ ] Test suite passes against both memory and PostgreSQL adapters.
- [ ] Concurrent tests prove no over-reservation or negative balance.
- [ ] Kill/restart test preserves orders, fills, balances, idempotency, and audit trail.
- [ ] Restore test reconstructs the state and passes the audit endpoint.
- [ ] No production database or secrets are placed in source control.

## Stage 3 — Offline deployment appliance

Produce an installable bundle for an existing compatible Linux host. It must include pinned dependencies and images, a local configuration template, offline preflight, installation, health checks, backup, restore, upgrade, and rollback. Network isolation is tested by disabling outbound connectivity after importing the bundle. Docker and a compatible host kernel remain prerequisites at this stage.

## Stage 4 — AION-owned operating system distribution

A portable container bundle is **not** an operating system. An OS requires a boot chain, kernel, init/service manager, users and permissions, filesystem layout, device drivers, package/image management, security updates, logging, recovery, and an installer.

Recommended incremental approach:
1. Start from a reproducible, source-available Linux distribution and its supported kernel/toolchain; maintain a pinned source mirror and signed package repository under AION control.
2. Build a minimal bootable ISO/VM image using reproducible recipes, with no runtime call-home requirement.
3. Add an immutable or rollback-capable base image, signed AION packages, local account management, firewall defaults, encrypted storage options, audit logs, and recovery environment.
4. Package SI Exchange as a service with local health checks, backup/restore, and offline installation.
5. Run VM boot tests, installation tests, network-disconnected tests, update/rollback tests, filesystem corruption/recovery tests, and security review.
6. Only after repeatable VM results, test on selected physical hardware and document the exact supported hardware matrix.

The OS can be independent of external service availability for its core boot and local operation, but no practical system is independent of all external requirements forever: hardware firmware, compatible drivers, security maintenance, and optional network services still exist. The goal is control over source, builds, signing keys, package mirrors, deployment, and local operation—not an unsupported claim of absolute independence.

## Stage 5 — AION-controlled infrastructure and operations

- AION-controlled source mirrors, build runners, artifact registry, package repository, signing and key-rotation policy.
- Reproducible builds from pinned source inputs.
- Monitoring and logs that work locally; remote reporting remains optional.
- Offline disaster-recovery copies and periodic restore drills.
- Documented upgrade windows, rollback criteria, vulnerability response, and ownership of every credential.

## Non-negotiable safety gates

- Keep the current production/default branch unchanged until the replacement has passed the stated gates.
- No real trading, deposits, withdrawals, custody, wallet keys, or real-money balances in this build.
- No spending or paid infrastructure without explicit approval.
- Do not store secrets, private keys, or recovery phrases in Git.
- A green CI run is evidence for the steps it actually executed, not proof of physical hardware compatibility, security certification, or production readiness.

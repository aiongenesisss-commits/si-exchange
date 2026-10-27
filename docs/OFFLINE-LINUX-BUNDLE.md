# Portable Linux bundle (simulation only)

## Purpose

Package a previously built SI Exchange container image and its source tree so a
separate Linux host can import and run the simulation without downloading the
container image or Python packages at startup.

## Current verified baseline

The Debian container build, existing test suite, and application health-route
registration passed in GitHub Actions run
https://github.com/aiongenesisss-commits/si-exchange/actions/runs/40472877656
for commit `fe55ca71fb8a65622480439e8a8e0e45ba0d1f59`.

This does **not** mean the bundle export script has already been executed or
that an offline host has been tested. The export must be run against a locally
built and tested image, then the resulting archive must be imported and
smoke-tested on a disconnected host before claiming full offline readiness.

## Export on a Linux machine with Docker

1. Build the image: `docker build -t si-exchange-linux:local .`
2. Run tests: `docker run --rm si-exchange-linux:local python -m pytest`
3. Export: `bash scripts/export_linux_bundle.sh`
4. Transfer `dist/si-exchange-linux-bundle.tar.gz` through a trusted channel.
5. On the target host, verify the outer archive checksum supplied by the sender.
6. Extract it, verify `SHA256SUMS`, then load `si-exchange-image.tar` with Docker.
7. From the included `source` directory, run `docker compose up -d` and verify
   `http://127.0.0.1:8000/health` locally.

The outer archive checksum must be conveyed separately to the recipient to
authenticate the archive; a checksum stored only inside the same archive is
not sufficient by itself.

## Boundaries

- This is a portable container bundle, not a standalone operating system.
- Docker and a compatible Linux kernel/host are still required.
- Live market data may be unavailable offline; the exchange simulation should
  remain usable without it if its application code does not require a remote
  market-data call during startup or order matching.
- No real trading, deposits, withdrawals, custody, or real-money balances are
  enabled by this bundle.
- Never include credentials, private keys, seed phrases, or production secrets.
- Do not deploy publicly or connect real money until persistence, authentication,
  authorization, auditability, backup/restore, concurrency, and security testing
  are implemented and independently reviewed.

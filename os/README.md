# AION Offline OS — first bootable prototype

This Debian Live-based x86_64 ISO prototype targets virtual-machine testing first. It is intended to include the SI Exchange simulation and a local Python environment, with runtime operation that does not require public internet access for the dashboard or health endpoint.

## Status

The build workflow and image are not yet validated. Building requires external Debian package repositories and Python package indexes. The image is intended to run offline after its dependencies are bundled; this is not a claim of absolute independence or production hardening.

## Safety

Simulation only: no live trading, deposits, withdrawals, custody, wallet signing, or real-money functionality. PostgreSQL is not configured by default. Physical hardware, secure boot, disconnected recovery, and update rollback still require separate testing.

#!/usr/bin/env python3
"""Validate AION network metadata without implying that a network is live."""
from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "networks" / "aion_networks.json"


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    networks = data.get("networks")
    if not isinstance(networks, list) or len(networks) != 2:
        return ["networks must contain exactly the two planned AION networks"]

    keys: set[str] = set()
    names: set[str] = set()
    chain_ids: set[int] = set()
    for network in networks:
        for field in (
            "key", "name", "chain_id", "rpc_url_env", "explorer_url_env",
            "token_address_env", "local_rpc_url", "public_rpc_url",
            "explorer_url", "token_deployed", "token_contract_address", "status",
        ):
            if field not in network:
                errors.append(f"network missing required field: {field}")
        if not all(field in network for field in ("key", "name", "chain_id")):
            continue
        if network["key"] in keys:
            errors.append(f"duplicate network key: {network['key']}")
        if network["name"] in names:
            errors.append(f"duplicate network name: {network['name']}")
        if network["chain_id"] in chain_ids:
            errors.append(f"duplicate chain ID: {network['chain_id']}")
        keys.add(network["key"])
        names.add(network["name"])
        chain_ids.add(network["chain_id"])
        if not isinstance(network["chain_id"], int) or isinstance(network["chain_id"], bool) or network["chain_id"] <= 0:
            errors.append(f"invalid chain ID for {network['name']}")
        if network["status"] not in {"planned", "testnet", "live"}:
            errors.append(f"invalid status for {network['name']}")
        if network["status"] == "live":
            errors.append(
                f"{network['name']} cannot be marked live by metadata alone; "
                "require external RPC, explorer, chain ID, and contract verification checks"
            )
        if network["status"] == "planned":
            if not isinstance(network.get("local_rpc_url"), str) or not network["local_rpc_url"].startswith("http://127.0.0.1:"):
                errors.append(f"{network['name']} local RPC must be loopback-only")
            if network.get("public_rpc_url") is not None or network.get("explorer_url") is not None:
                errors.append(f"{network['name']} must not claim public RPC or explorer URLs while planned")
            if network.get("token_deployed") is not False or network.get("token_contract_address") is not None:
                errors.append(f"{network['name']} must not claim a deployed token while planned")

    free = data.get("free_deployments", {})
    if free.get("limit_per_network") != 50:
        errors.append("free deployment limit must remain 50 per network")
    if free.get("status") != "not_enabled":
        errors.append("free deployments must remain disabled until the gas sponsor and abuse controls are implemented")
    if free.get("status") == "enabled" and not all(
        free.get(field) is True
        for field in ("requires_sponsored_gas", "requires_rate_limits", "requires_auditable_counter")
    ):
        errors.append("free deployments cannot be enabled without sponsored gas, rate limits, and an auditable counter")
    if data.get("status") != "configuration_only":
        errors.append("registry must remain configuration_only until public launch verification is implemented")
    return errors


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read valid JSON from {path}: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {path} is valid; AION Nova and AION Orbit remain planned, not live.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

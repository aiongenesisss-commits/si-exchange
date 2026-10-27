#!/usr/bin/env python3
"""Smoke-test local AION Anvil devnets. This never deploys contracts or spends funds."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "networks" / "aion_networks.json"
EXPECTED = {"AION Nova": 71101, "AION Orbit": 71102}
RPCS = {
    "AION Nova": os.getenv("AION_NOVA_RPC_URL", "http://127.0.0.1:8545"),
    "AION Orbit": os.getenv("AION_ORBIT_RPC_URL", "http://127.0.0.1:8546"),
}


def rpc(url: str, method: str) -> object:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": []}).encode()
    request = Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=3) as response:
        body = json.loads(response.read().decode("utf-8"))
    if "error" in body:
        raise RuntimeError(f"JSON-RPC {method} returned an error")
    return body.get("result")


def validate_registry() -> list[dict]:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    networks = data.get("networks", [])
    if len(networks) != 2:
        raise AssertionError("Expected exactly two configured AION networks")
    if {item.get("name"): item.get("chain_id") for item in networks} != EXPECTED:
        raise AssertionError("Canonical registry names and chain IDs do not match Nova/Orbit")
    if data.get("status") != "configuration_only":
        raise AssertionError("Registry must remain configuration_only until public launch is verified")
    for item in networks:
        name = item.get("name")
        if item.get("status") != "planned":
            raise AssertionError(f"{name} must remain planned until verified public deployment")
        if item.get("public_rpc_url") is not None or item.get("explorer_url") is not None:
            raise AssertionError(f"{name} must not claim public RPC or explorer endpoints")
        if item.get("token_deployed") is not False or item.get("token_contract_address") is not None:
            raise AssertionError(f"{name} must not claim a deployed token")
    promotion = data.get("free_deployments", {})
    if promotion.get("status") != "not_enabled":
        raise AssertionError("Free deployment promotion must remain disabled until implemented")
    for control in ("requires_sponsored_gas", "requires_rate_limits", "requires_auditable_counter"):
        if promotion.get(control) is not True:
            raise AssertionError(f"Free deployment promotion lacks required control: {control}")
    return networks


def main() -> int:
    try:
        networks = validate_registry()
    except Exception as exc:
        print(f"CONFIG FAIL: {exc}", file=sys.stderr)
        return 1

    for item in networks:
        name = item["name"]
        url = RPCS[name]
        expected = EXPECTED[name]
        deadline = time.monotonic() + int(os.getenv("AION_RPC_WAIT_SECONDS", "60"))
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                chain_hex = rpc(url, "eth_chainId")
                actual = int(str(chain_hex), 16)
            except (OSError, URLError, HTTPError, TimeoutError, ValueError, RuntimeError) as exc:
                last_error = exc
                time.sleep(1)
                continue

            # A responding node on the wrong chain is a configuration error, not a startup delay.
            if actual != expected:
                print(f"RPC FAIL {name} ({url}): expected chain ID {expected}, got {actual}", file=sys.stderr)
                return 1

            try:
                block_hex = rpc(url, "eth_blockNumber")
                client = rpc(url, "web3_clientVersion")
                if not isinstance(block_hex, str) or not isinstance(client, str) or not client:
                    raise RuntimeError("incomplete JSON-RPC health information")
            except (OSError, URLError, HTTPError, TimeoutError, ValueError, RuntimeError) as exc:
                last_error = exc
                time.sleep(1)
                continue

            print(f"PASS {name}: chain_id={actual}, block={int(block_hex, 16)}, client={client}")
            break
        else:
            print(f"RPC FAIL {name} ({url}): {last_error}", file=sys.stderr)
            return 1

    print("PASS registry: unique chain IDs, no claimed public endpoints/token deployment, promotion disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

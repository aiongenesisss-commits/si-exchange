#!/usr/bin/env python3
"""Smoke-test local AION Anvil devnets. This never deploys contracts or spends funds."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "aion-networks.json"
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


def validate_manifest() -> list[dict]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    networks = config.get("networks", [])
    if len(networks) != 2:
        raise AssertionError("Expected exactly two configured AION networks")
    ids = [item.get("chain_id") for item in networks]
    if len(set(ids)) != len(ids) or set(ids) != set(EXPECTED.values()):
        raise AssertionError(f"Network chain IDs must be unique and equal to {sorted(EXPECTED.values())}")
    if config.get("production_deployment_verified") is not False:
        raise AssertionError("Manifest must not claim production deployment is verified")
    for item in networks:
        if item.get("public_rpc_url") is not None or item.get("token_deployed") is not False:
            raise AssertionError(f"{item.get('name')} must not claim a public RPC or deployed token")
    promo = config.get("free_deployment_promotion", {})
    if promo.get("enabled") is not False or promo.get("public_claim_allowed") is not False:
        raise AssertionError("The free-deployment promotion must stay disabled until implemented")
    return networks


def main() -> int:
    try:
        networks = validate_manifest()
    except Exception as exc:
        print(f"CONFIG FAIL: {exc}", file=sys.stderr)
        return 1

    for item in networks:
        name = item["name"]
        url = RPCS[name]
        expected = EXPECTED[name]
        deadline = time.monotonic() + int(os.getenv("AION_RPC_WAIT_SECONDS", "90"))
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                chain_hex = rpc(url, "eth_chainId")
                block_hex = rpc(url, "eth_blockNumber")
                client = rpc(url, "web3_clientVersion")
                actual = int(str(chain_hex), 16)
                if actual != expected:
                    raise AssertionError(f"{name} expected chain ID {expected}, got {actual}")
                if not isinstance(block_hex, str) or not isinstance(client, str) or not client:
                    raise AssertionError(f"{name} returned incomplete JSON-RPC health information")
                print(f"PASS {name}: chain_id={actual}, block={int(block_hex, 16)}, client={client}")
                break
            except (OSError, URLError, HTTPError, TimeoutError, ValueError, RuntimeError, AssertionError) as exc:
                last_error = exc
                time.sleep(1)
        else:
            print(f"RPC FAIL {name} ({url}): {last_error}", file=sys.stderr)
            return 1

    print("PASS manifest: unique chain IDs, no claimed public RPC/token deployment, promotion disabled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

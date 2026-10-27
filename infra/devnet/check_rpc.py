#!/usr/bin/env python3
"""Smoke-test the local AION Nova and Orbit Anvil nodes; uses only Python stdlib."""
import json
import sys
import time
import urllib.error
import urllib.request

NODES = {
    "AION Nova": ("http://127.0.0.1:18545", 71101),
    "AION Orbit": ("http://127.0.0.1:18546", 71102),
}


def rpc(url, method, params=None):
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": method, "params": params or []
    }).encode()
    request = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=3) as response:
        result = json.loads(response.read())
    if "error" in result:
        raise RuntimeError(f"{method}: {result['error']}")
    return result["result"]


def main():
    for _ in range(20):
        try:
            for name, (url, expected_chain_id) in NODES.items():
                actual = int(rpc(url, "eth_chainId"), 16)
                if actual != expected_chain_id:
                    raise RuntimeError(
                        f"{name}: expected chain ID {expected_chain_id}, got {actual}"
                    )
            break
        except (OSError, urllib.error.URLError, TimeoutError):
            time.sleep(1)
    else:
        print("FAIL: one or both RPC endpoints did not become ready", file=sys.stderr)
        return 1

    nova_url = NODES["AION Nova"][0]
    orbit_url = NODES["AION Orbit"][0]
    nova_before = int(rpc(nova_url, "eth_blockNumber"), 16)
    orbit_before = int(rpc(orbit_url, "eth_blockNumber"), 16)
    rpc(nova_url, "evm_mine")
    nova_after = int(rpc(nova_url, "eth_blockNumber"), 16)
    orbit_after = int(rpc(orbit_url, "eth_blockNumber"), 16)

    if nova_after <= nova_before:
        print("FAIL: mining did not advance Nova", file=sys.stderr)
        return 1
    if orbit_after != orbit_before:
        print("FAIL: mining Nova unexpectedly changed Orbit", file=sys.stderr)
        return 1

    print("PASS: Nova chain ID 71101 responds and mines independently")
    print("PASS: Orbit chain ID 71102 responds and remains isolated")
    print("NOTE: local disposable development nodes only; not public networks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

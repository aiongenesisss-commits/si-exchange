#!/usr/bin/env python3
"""Read-only JSON-RPC smoke check for the isolated AION Nova/Orbit devnet."""
import json
import os
import sys
import urllib.error
import urllib.request

NETWORKS = (
    ("AION Nova", os.getenv("AION_NOVA_RPC_URL", "http://127.0.0.1:18545"), 71101),
    ("AION Orbit", os.getenv("AION_ORBIT_RPC_URL", "http://127.0.0.1:18546"), 71102),
)


def rpc_chain_id(url: str) -> int:
    payload = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_chainId",
        "params": [],
    }).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        result = json.loads(response.read().decode("utf-8"))
    if "error" in result:
        raise RuntimeError(f"JSON-RPC error: {result['error']}")
    value = result.get("result")
    if not isinstance(value, str) or not value.startswith("0x"):
        raise RuntimeError(f"Unexpected eth_chainId result: {value!r}")
    return int(value, 16)


def main() -> int:
    failed = False
    for name, url, expected in NETWORKS:
        try:
            actual = rpc_chain_id(url)
            if actual != expected:
                print(f"FAIL {name}: expected chain ID {expected}, got {actual} ({url})")
                failed = True
            else:
                print(f"PASS {name}: JSON-RPC reachable; chain ID {actual} ({url})")
        except (OSError, urllib.error.URLError, TimeoutError, ValueError, RuntimeError) as exc:
            print(f"FAIL {name}: {url}: {exc}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

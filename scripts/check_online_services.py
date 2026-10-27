#!/usr/bin/env python3
"""Read-only HTTPS reachability monitor for explicitly configured AION endpoints."""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

SERVICES = {
    "SI Exchange": "AION_EXCHANGE_URL",
    "AION Nova RPC health": "AION_NOVA_RPC_HEALTH_URL",
    "AION Orbit RPC health": "AION_ORBIT_RPC_HEALTH_URL",
    "AION Coin explorer": "AION_COIN_EXPLORER_URL",
}


def check(name: str, variable: str) -> bool:
    url = os.getenv(variable, "").strip()
    if not url:
        print(f"NOT_CONFIGURED | {name} | {variable}")
        return True  # Missing future services are informational, not a false CI failure.
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        print(f"INVALID_URL | {name} | expected public HTTPS URL in {variable}")
        return False
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "AION-Online-Readiness/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            status = response.status
            ok = 200 <= status < 400
            print(f"{'REACHABLE' if ok else 'HTTP_ERROR'} | {name} | HTTP {status} | {url}")
            return ok
    except urllib.error.HTTPError as exc:
        print(f"HTTP_ERROR | {name} | HTTP {exc.code} | {url}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        reason = getattr(exc, "reason", exc)
        print(f"UNREACHABLE | {name} | {type(reason).__name__} | {url}")
    return False


def main() -> int:
    results = [check(name, variable) for name, variable in SERVICES.items()]
    failed = len(results) - sum(results)
    print(f"SUMMARY | configured checks failing: {failed} | total services: {len(results)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

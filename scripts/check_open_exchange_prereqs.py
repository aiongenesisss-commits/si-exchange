#!/usr/bin/env python3
"""Read-only prerequisite checker for the isolated Open Exchange local POC.

This script does not install packages, start containers, change sysctls, open ports,
or contact any remote service. It only inspects the local OS, available memory,
shared-memory mount, and installed tool versions.
"""
from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

MINIMUMS = {
    "java": (21, 0, 0),
    "mvn": (3, 9, 0),
    "go": (1, 25, 0),
    "node": (22, 22, 0),
    "python3": (3, 10, 0),
}


def version_tuple(text: str) -> tuple[int, int, int] | None:
    match = re.search(r"(?<!\d)(\d+)\.(\d+)(?:\.(\d+))?", text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2)), int(match.group(3) or 0)


def command_version(command: str, args: list[str]) -> dict[str, Any]:
    executable = shutil.which(command)
    if not executable:
        return {"available": False, "ok": False, "detail": "not installed or not on PATH"}
    try:
        result = subprocess.run(
            [executable, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        first_line = next((line.strip() for line in output.splitlines() if line.strip()), "")
        parsed = version_tuple(output)
        minimum = MINIMUMS.get(command)
        version_ok = parsed is not None and (minimum is None or parsed >= minimum)
        ok = result.returncode == 0 and version_ok
        detail = first_line[:240] or f"exit code {result.returncode}"
        if minimum and parsed is not None and parsed < minimum:
            detail += f" (requires >= {'.'.join(map(str, minimum))})"
        elif parsed is None:
            detail += " (could not parse version)"
        return {
            "available": True,
            "ok": ok,
            "version": ".".join(map(str, parsed)) if parsed else None,
            "detail": detail,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": True, "ok": False, "detail": str(exc)[:240]}


def main() -> int:
    checks: dict[str, Any] = {}
    is_linux = platform.system() == "Linux"
    checks["linux"] = {"ok": is_linux, "detail": platform.platform()}
    checks["tools"] = {
        "java": command_version("java", ["-version"]),
        "mvn": command_version("mvn", ["-version"]),
        "go": command_version("go", ["version"]),
        "node": command_version("node", ["--version"]),
        "python3": command_version("python3", ["--version"]),
        "npm": command_version("npm", ["--version"]),
        "git": command_version("git", ["--version"]),
        "psql": command_version("psql", ["--version"]),
        "docker": command_version("docker", ["--version"]),
    }

    mem_total_bytes = None
    mem_available_bytes = None
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        values: dict[str, int] = {}
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            match = re.match(r"^(MemTotal|MemAvailable):\s+(\d+)\s+kB", line)
            if match:
                values[match.group(1)] = int(match.group(2)) * 1024
        mem_total_bytes = values.get("MemTotal")
        mem_available_bytes = values.get("MemAvailable")
    checks["memory"] = {
        "ok": bool(mem_available_bytes and mem_available_bytes >= 8 * 1024**3),
        "available_gib": round(mem_available_bytes / 1024**3, 2) if mem_available_bytes else None,
        "required_available_gib": 8,
        "detail": "Available RAM from /proc/meminfo; container limits may differ.",
    }

    shm = Path("/dev/shm")
    checks["shared_memory"] = {
        "ok": shm.is_dir() and os.access(shm, os.W_OK),
        "detail": "Writable /dev/shm required by the local demo." if shm.is_dir() else "/dev/shm missing",
    }

    docker = checks["tools"]["docker"]
    if docker["available"]:
        info = subprocess.run(
            [shutil.which("docker") or "docker", "info", "--format", "{{.ServerVersion}}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=8,
        )
        checks["docker_daemon"] = {
            "ok": info.returncode == 0 and bool(info.stdout.strip()),
            "detail": info.stdout.strip() if info.returncode == 0 else (info.stderr.strip()[:240] or "Docker daemon unavailable"),
        }
    else:
        checks["docker_daemon"] = {"ok": False, "detail": "Docker CLI unavailable"}

    failed = []
    for name, result in checks.items():
        if name == "tools":
            for tool, state in result.items():
                if not state["ok"]:
                    failed.append(f"tool:{tool}")
        elif not result["ok"]:
            failed.append(name)

    print(json.dumps({"status": "ready" if not failed else "not_ready", "checks": checks, "failed": failed}, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
set -Eeuo pipefail
ISO="${1:-dist/aion-offline-os-amd64.iso}"
[[ -f "$ISO" ]] || { echo "ISO not found: $ISO" >&2; exit 2; }
command -v qemu-system-x86_64 >/dev/null 2>&1 || { echo "qemu-system-x86_64 is required." >&2; exit 2; }
command -v curl >/dev/null 2>&1 || { echo "curl is required." >&2; exit 2; }
LOG="$(mktemp)"
QEMU_LOG="$(mktemp)"
PID=""
cleanup() {
  if [[ -n "$PID" ]]; then kill "$PID" >/dev/null 2>&1 || true; wait "$PID" >/dev/null 2>&1 || true; fi
  rm -f "$LOG" "$QEMU_LOG"
}
trap cleanup EXIT
qemu-system-x86_64 \
  -machine q35 -m 2048 -smp 2 -display none -serial "file:$QEMU_LOG" -monitor none \
  -netdev user,id=net0,hostfwd=tcp:127.0.0.1:18000-:8000 \
  -device e1000,netdev=net0 -cdrom "$ISO" -boot d -no-reboot >"$LOG" 2>&1 &
PID=$!
for _ in $(seq 1 75); do
  if curl --silent --show-error --fail --max-time 2 http://127.0.0.1:18000/health >"$LOG.health" 2>/dev/null; then
    grep -q '"status":"ok"' "$LOG.health"
    grep -q '"mode":"simulation_only"' "$LOG.health"
    echo "QEMU ISO smoke test passed: guest /health responded in simulation-only mode."
    exit 0
  fi
  if ! kill -0 "$PID" >/dev/null 2>&1; then
    echo "QEMU exited before the health endpoint became available." >&2
    cat "$LOG" >&2 || true
    cat "$QEMU_LOG" >&2 || true
    exit 1
  fi
  sleep 2
done
echo "Timed out waiting for the guest health endpoint." >&2
cat "$LOG" >&2 || true
cat "$QEMU_LOG" >&2 || true
exit 1

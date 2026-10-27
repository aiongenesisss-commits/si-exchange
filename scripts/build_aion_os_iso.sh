#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/dist"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
for tool in lb debootstrap mksquashfs xorriso grub-mkstandalone qemu-system-x86_64 docker; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing build tool: $tool" >&2; exit 2; }
done
mkdir -p "$OUT"
cp -a "$ROOT/os/live-build/config" "$WORK/config"
INCLUDES="$WORK/config/includes.chroot/opt/aion"
mkdir -p "$INCLUDES/si-exchange" "$INCLUDES/wheelhouse"
cp -a "$ROOT/app" "$INCLUDES/si-exchange/app"
cp "$ROOT/requirements-os.txt" "$INCLUDES/requirements-os.txt"
cp "$ROOT/migrations/001_initial_schema.sql" "$INCLUDES/si-exchange/001_initial_schema.sql"
# Build the wheelhouse with the target OS Python version, not the Ubuntu host's Python.
docker run --rm \
  -v "$INCLUDES/wheelhouse:/wheelhouse" \
  -v "$ROOT/requirements-os.txt:/requirements-os.txt:ro" \
  python:3.11-slim-bookworm \
  python -m pip download --only-binary=:all: --dest /wheelhouse -r /requirements-os.txt
(
  cd "$WORK"
  chmod 0755 config/hooks/live/010-install-aion.hook.chroot
  lb config \
    --ignore-system-defaults \
    --distribution bookworm \
    --architectures amd64 \
    --keyring-packages debian-archive-keyring \
    --linux-packages linux-image \
    --linux-flavours amd64 \
    --binary-images iso-hybrid \
    --archive-areas "main" \
    --mirror-bootstrap "http://deb.debian.org/debian/" \
    --mirror-chroot "http://deb.debian.org/debian/" \
    --mirror-binary "http://deb.debian.org/debian/" \
    --mirror-chroot-security "http://security.debian.org/debian-security/" \
    --mirror-binary-security "http://security.debian.org/debian-security/" \
    --apt-recommends false \
    --bootappend-live "boot=live components quiet console=ttyS0,115200n8"
  lb build
)
ISO="$(find "$WORK" -maxdepth 2 -type f -name '*.iso' -print -quit)"
[[ -n "$ISO" ]] || { echo "No ISO was produced by live-build." >&2; exit 1; }
cp "$ISO" "$OUT/aion-offline-os-amd64.iso"
(cd "$OUT" && sha256sum aion-offline-os-amd64.iso > aion-offline-os-amd64.iso.sha256)
echo "Built: $OUT/aion-offline-os-amd64.iso"

#!/usr/bin/env bash
set -Eeuo pipefail

SOURCE_IMAGE="${SI_EXCHANGE_IMAGE:-si-exchange-linux:local}"
BUNDLE_IMAGE="${SI_EXCHANGE_BUNDLE_IMAGE:-si-exchange-linux:local}"
OUT_DIR="${SI_EXCHANGE_OUT_DIR:-dist/si-exchange-linux-bundle}"

command -v docker >/dev/null 2>&1 || { echo "ERROR: Docker CLI is required." >&2; exit 2; }
command -v sha256sum >/dev/null 2>&1 || { echo "ERROR: sha256sum is required." >&2; exit 2; }
docker image inspect "$SOURCE_IMAGE" >/dev/null 2>&1 || {
  echo "ERROR: image '$SOURCE_IMAGE' is not present locally. Build and test it first." >&2
  exit 2
}

rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR/source"

docker image tag "$SOURCE_IMAGE" "$BUNDLE_IMAGE"
docker save --output "$OUT_DIR/si-exchange-image.tar" "$BUNDLE_IMAGE"
for path in Dockerfile compose.yaml requirements.txt requirements-dev.txt pyproject.toml README.md app api tests scripts; do
  if [[ -e "$path" ]]; then
    cp -a "$path" "$OUT_DIR/source/"
  fi
done

cat > "$OUT_DIR/README-OFFLINE.txt" <<'EOF'
AION SI Exchange — offline simulation bundle

1. Verify files: sha256sum -c SHA256SUMS
2. Load the image: docker load --input si-exchange-image.tar
3. Run from the source directory: cd source && docker compose up -d
4. Open the app on the same machine at http://127.0.0.1:8000

This package is simulation-only. It does not enable real trading, deposits,
withdrawals, custody, or real-money balances. The UI may not have live market
prices when disconnected from the internet. Protect this bundle and its data.
EOF

(
  cd "$OUT_DIR"
  find si-exchange-image.tar README-OFFLINE.txt source -type f -print0 \
    | sort -z \
    | xargs -0 sha256sum > SHA256SUMS
)
tar -czf "${OUT_DIR}.tar.gz" -C "$(dirname "$OUT_DIR")" "$(basename "$OUT_DIR")"
sha256sum "${OUT_DIR}.tar.gz"
echo "Bundle created: ${OUT_DIR}.tar.gz"

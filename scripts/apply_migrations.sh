#!/usr/bin/env bash
set -Eeuo pipefail
: "${DATABASE_URL:?Set DATABASE_URL to the target PostgreSQL database}"
MIGRATION="${SI_EXCHANGE_MIGRATION:-migrations/001_initial_schema.sql}"
[[ -f "$MIGRATION" ]] || { echo "ERROR: migration not found: $MIGRATION" >&2; exit 2; }
command -v psql >/dev/null 2>&1 || { echo "ERROR: psql is required." >&2; exit 2; }
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$MIGRATION"
echo "Migration applied. Next start the app with AION_STORAGE_BACKEND=postgres and the same DATABASE_URL."

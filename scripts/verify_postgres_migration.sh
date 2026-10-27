#!/usr/bin/env bash
set -Eeuo pipefail

command -v docker >/dev/null 2>&1 || { echo "ERROR: Docker is required." >&2; exit 2; }
MIGRATION="${SI_EXCHANGE_MIGRATION:-migrations/001_initial_schema.sql}"
[[ -f "$MIGRATION" ]] || { echo "ERROR: migration not found: $MIGRATION" >&2; exit 2; }

NAME="si-exchange-pg-verify-$RANDOM-$RANDOM"
PORT="${SI_EXCHANGE_PG_PORT:-55439}"
PASSWORD="temporary-verification-only"

cleanup() { docker rm -f "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

docker run -d --name "$NAME" -e POSTGRES_PASSWORD="$PASSWORD" -e POSTGRES_DB=si_exchange_verify -p "127.0.0.1:$PORT:5432" postgres:16-alpine >/dev/null

ready=0
for _ in $(seq 1 60); do
  if docker exec "$NAME" pg_isready -U postgres -d si_exchange_verify >/dev/null 2>&1; then ready=1; break; fi
  sleep 1
done
[[ "$ready" == 1 ]] || { echo "ERROR: temporary PostgreSQL did not become ready." >&2; exit 1; }

docker exec -i "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d si_exchange_verify < "$MIGRATION"

tables="$(docker exec "$NAME" psql -At -U postgres -d si_exchange_verify -c "SELECT count(*) FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('demo_accounts','demo_balances','demo_orders','demo_fills','demo_idempotency_keys','demo_audit_events')")"
[[ "$tables" == "6" ]] || { echo "ERROR: expected 6 schema tables; found $tables." >&2; exit 1; }

# Prove the demo-only account constraint rejects a non-demo account.
if docker exec "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d si_exchange_verify -c "INSERT INTO demo_accounts(id,label,account_type) VALUES ('unsafe','must fail','real')" >/dev/null 2>&1; then
  echo "ERROR: schema accepted a non-demo account type." >&2
  exit 1
fi

echo "PostgreSQL migration applied; six expected tables exist; demo-only constraint rejected a non-demo account."

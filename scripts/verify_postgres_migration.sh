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
  if docker exec "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d si_exchange_verify -c "SELECT 1" >/dev/null 2>&1; then ready=1; break; fi
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

# Reapply the migration to prove IF NOT EXISTS behavior is repeatable.
docker exec -i "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d si_exchange_verify < "$MIGRATION" >/dev/null

# Exercise the demo-only schema relationships and fixed-precision columns.
docker exec -i "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d si_exchange_verify <<'SQL'
INSERT INTO demo_accounts(id,label,account_type) VALUES ('A','Demo A','demo'),('B','Demo B','demo');
INSERT INTO demo_balances(account_id,asset,available_amount) VALUES ('A','SAR',10000),('A','BTC',1),('B','SAR',10000),('B','BTC',1);
INSERT INTO demo_orders(id,account_id,market,side,limit_price,quantity,remaining_quantity,status,created_at)
VALUES
('00000000-0000-4000-8000-000000000001','A','BTC/SAR','buy',250000,0.01,0.01,'open',now()),
('00000000-0000-4000-8000-000000000002','B','BTC/SAR','sell',250000,0.01,0.01,'open',now());
INSERT INTO demo_fills(id,market,maker_order_id,taker_order_id,buyer_account_id,seller_account_id,execution_price,quantity,simulated_value_sar,created_at)
VALUES ('00000000-0000-4000-8000-000000000003','BTC/SAR','00000000-0000-4000-8000-000000000001','00000000-0000-4000-8000-000000000002','A','B',250000,0.01,2500,now());
INSERT INTO demo_idempotency_keys(key,request_fingerprint,order_id)
VALUES ('verify-key','fingerprint','00000000-0000-4000-8000-000000000001');
INSERT INTO demo_audit_events(event_type,entity_type,entity_id,details)
VALUES ('schema_verify','order','00000000-0000-4000-8000-000000000001','{"mode":"simulation_only"}');
SQL

if docker exec "$NAME" psql -v ON_ERROR_STOP=1 -U postgres -d si_exchange_verify -c "INSERT INTO demo_balances(account_id,asset,available_amount) VALUES ('A','ETH',-1)" >/dev/null 2>&1; then
  echo "ERROR: schema accepted a negative demo balance." >&2
  exit 1
fi

echo "PostgreSQL migration applied twice; six expected tables exist; demo-only account and nonnegative-balance constraints passed; demo relationships accepted valid sample records."

-- SI Exchange persistence foundation (PostgreSQL)
-- Simulation-only schema. This migration does not enable deposits, withdrawals,
-- custody, wallet keys, blockchain access, or live trading.
BEGIN;

CREATE TABLE IF NOT EXISTS demo_accounts (
    id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    account_type TEXT NOT NULL DEFAULT 'demo' CHECK (account_type = 'demo'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS demo_balances (
    account_id TEXT NOT NULL REFERENCES demo_accounts(id),
    asset TEXT NOT NULL CHECK (asset ~ '^[A-Z0-9]{2,12}$'),
    available_amount NUMERIC(38, 12) NOT NULL DEFAULT 0 CHECK (available_amount >= 0),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (account_id, asset)
);

CREATE TABLE IF NOT EXISTS demo_orders (
    id UUID PRIMARY KEY,
    account_id TEXT NOT NULL REFERENCES demo_accounts(id),
    market TEXT NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('buy', 'sell')),
    limit_price NUMERIC(38, 12) NOT NULL CHECK (limit_price > 0),
    quantity NUMERIC(38, 12) NOT NULL CHECK (quantity > 0),
    remaining_quantity NUMERIC(38, 12) NOT NULL CHECK (remaining_quantity >= 0 AND remaining_quantity <= quantity),
    status TEXT NOT NULL CHECK (status IN ('open', 'partially_filled', 'filled', 'cancelled')),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_demo_orders_book
    ON demo_orders (market, side, status, limit_price, created_at);

CREATE TABLE IF NOT EXISTS demo_fills (
    id UUID PRIMARY KEY,
    market TEXT NOT NULL,
    maker_order_id UUID NOT NULL REFERENCES demo_orders(id),
    taker_order_id UUID NOT NULL REFERENCES demo_orders(id),
    buyer_account_id TEXT NOT NULL REFERENCES demo_accounts(id),
    seller_account_id TEXT NOT NULL REFERENCES demo_accounts(id),
    execution_price NUMERIC(38, 12) NOT NULL CHECK (execution_price > 0),
    quantity NUMERIC(38, 12) NOT NULL CHECK (quantity > 0),
    simulated_value_sar NUMERIC(38, 12) NOT NULL CHECK (simulated_value_sar > 0),
    created_at TIMESTAMPTZ NOT NULL,
    CHECK (maker_order_id <> taker_order_id),
    CHECK (buyer_account_id <> seller_account_id)
);
CREATE INDEX IF NOT EXISTS idx_demo_fills_created_at ON demo_fills (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_demo_fills_market ON demo_fills (market, created_at DESC);

CREATE TABLE IF NOT EXISTS demo_idempotency_keys (
    key TEXT PRIMARY KEY CHECK (length(key) BETWEEN 1 AND 200),
    request_fingerprint TEXT NOT NULL,
    order_id UUID NOT NULL REFERENCES demo_orders(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS demo_audit_events (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    event_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_demo_audit_entity ON demo_audit_events (entity_type, entity_id, created_at DESC);

COMMIT;

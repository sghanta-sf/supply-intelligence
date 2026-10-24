-- App-owned notes for recommended purchase orders.
-- Separate from recommended_orders so comments survive lakehouse sync and do not
-- require ALTER on a table the app SP may not own.

CREATE TABLE IF NOT EXISTS supply_intel.recommended_order_comments (
    recommendation_id INTEGER PRIMARY KEY,
    comments TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_by TEXT
);

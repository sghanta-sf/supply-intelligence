-- Apex Healthcare Supply Intelligence Schema
-- Lakebase Autoscaling (PostgreSQL 17)

CREATE SCHEMA IF NOT EXISTS supply_intel AUTHORIZATION CURRENT_USER;

-- 1. Risk-scored items (ML model output from Lakehouse Gold via Synced Tables)
CREATE TABLE IF NOT EXISTS supply_intel.risk_scores (
    item_id VARCHAR(20) PRIMARY KEY,
    item_description TEXT NOT NULL,
    item_category VARCHAR(50) NOT NULL,
    current_on_hand INTEGER NOT NULL DEFAULT 0,
    avg_daily_usage DECIMAL(8,2) NOT NULL DEFAULT 0.0,
    days_of_supply DECIMAL(5,1) NOT NULL DEFAULT 0.0,
    risk_score DECIMAL(5,2) NOT NULL DEFAULT 0.0,       -- 0-100 ML scored
    risk_tier VARCHAR(20) NOT NULL DEFAULT 'low',       -- critical, high, medium, low
    risk_factors JSONB NOT NULL DEFAULT '{}'::jsonb,    -- supplier reliability, lead time variance, port congestion, demand volatility
    forecast_demand_30d INTEGER NOT NULL DEFAULT 0,
    forecast_demand_90d INTEGER NOT NULL DEFAULT 0,
    last_scored_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Recommended orders (optimization model output synced from Lakehouse Gold)
CREATE TABLE IF NOT EXISTS supply_intel.recommended_orders (
    recommendation_id SERIAL PRIMARY KEY,
    item_id VARCHAR(20) NOT NULL,
    item_description TEXT NOT NULL,
    supplier_id VARCHAR(20) NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    recommended_qty INTEGER NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(12,2) NOT NULL,
    order_reason VARCHAR(50) NOT NULL,                  -- restock, shortage_prevention, safety_stock, recall_replacement
    urgency VARCHAR(20) NOT NULL DEFAULT 'routine',     -- routine, expedite, emergency
    confidence_score DECIMAL(5,2) NOT NULL DEFAULT 85.0,
    model_reasoning TEXT NOT NULL,
    facility_id VARCHAR(20) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3. Substitution candidates (clinical agent outputs synced from Lakehouse Gold)
CREATE TABLE IF NOT EXISTS supply_intel.substitution_candidates (
    substitution_id SERIAL PRIMARY KEY,
    shortage_item_id VARCHAR(20) NOT NULL,
    shortage_item_description TEXT NOT NULL,
    alternative_item_id VARCHAR(20) NOT NULL,
    alternative_item_description TEXT NOT NULL,
    clinical_equivalence VARCHAR(20) NOT NULL,          -- equivalent, similar, partial
    formulary_status VARCHAR(20) NOT NULL,              -- on_formulary, off_formulary, restricted
    availability VARCHAR(20) NOT NULL DEFAULT 'in_stock', -- in_stock, available_to_order, backordered
    agent_reasoning TEXT NOT NULL,
    confidence_score DECIMAL(5,2) NOT NULL DEFAULT 90.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. Recall items (FDA recalls matched against inventory and patient exposure)
CREATE TABLE IF NOT EXISTS supply_intel.recall_items (
    recall_id SERIAL PRIMARY KEY,
    fda_recall_number VARCHAR(50) NOT NULL,
    recall_class VARCHAR(10) NOT NULL,                  -- I, II, III
    item_id VARCHAR(20) NOT NULL,
    item_description TEXT NOT NULL,
    affected_lot VARCHAR(50) NOT NULL,
    facility_id VARCHAR(20) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    location_in_facility VARCHAR(100) NOT NULL,
    qty_on_hand INTEGER NOT NULL DEFAULT 0,
    patient_exposure_count INTEGER NOT NULL DEFAULT 0,
    recall_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open'          -- open, quarantined, resolved
);

-- 5. Transfer recommendations (inter-facility rebalancing)
CREATE TABLE IF NOT EXISTS supply_intel.transfer_recommendations (
    transfer_id SERIAL PRIMARY KEY,
    item_id VARCHAR(20) NOT NULL,
    item_description TEXT NOT NULL,
    from_facility_id VARCHAR(20) NOT NULL,
    from_facility_name VARCHAR(100) NOT NULL,
    to_facility_id VARCHAR(20) NOT NULL,
    to_facility_name VARCHAR(100) NOT NULL,
    recommended_qty INTEGER NOT NULL,
    reason VARCHAR(50) NOT NULL,                        -- rebalance, shortage_relief, expiration_prevention
    from_days_of_supply DECIMAL(5,1) NOT NULL,
    to_days_of_supply DECIMAL(5,1) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',      -- pending, approved, rejected
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 6. Inventory snapshot (real-time item x facility x lot level data)
CREATE TABLE IF NOT EXISTS supply_intel.inventory_snapshot (
    snapshot_id SERIAL PRIMARY KEY,
    item_id VARCHAR(20) NOT NULL,
    item_description TEXT NOT NULL,
    facility_id VARCHAR(20) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    location VARCHAR(100) NOT NULL,
    on_hand_qty INTEGER NOT NULL DEFAULT 0,
    lot_number VARCHAR(50) NOT NULL,
    expiration_date DATE NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL DEFAULT 0.0,
    last_updated TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, facility_id, lot_number)
);

-- 7. App-Owned: Order decisions (user approves/modifies/rejects recommendations)
CREATE TABLE IF NOT EXISTS supply_intel.order_decisions (
    decision_id SERIAL PRIMARY KEY,
    recommendation_id INTEGER NOT NULL,
    decision VARCHAR(20) NOT NULL,                     -- approved, modified, rejected
    modified_qty INTEGER,
    modified_supplier_id VARCHAR(20),
    decision_reason TEXT,
    decided_by VARCHAR(100) NOT NULL,
    decided_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 8. App-Owned: Substitution selections (pharmacist selection of clinical alternatives)
CREATE TABLE IF NOT EXISTS supply_intel.substitution_selections (
    selection_id SERIAL PRIMARY KEY,
    substitution_id INTEGER NOT NULL,
    shortage_item_id VARCHAR(20) NOT NULL,
    selected_alternative_id VARCHAR(20) NOT NULL,
    clinical_notes TEXT,
    selected_by VARCHAR(100) NOT NULL,
    selected_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 9. App-Owned: Recall actions (quarantine, patient trace, removal)
CREATE TABLE IF NOT EXISTS supply_intel.recall_actions (
    action_id SERIAL PRIMARY KEY,
    recall_id INTEGER NOT NULL,
    action_type VARCHAR(30) NOT NULL,                  -- quarantined, removed, traced_patients, acknowledged
    notes TEXT,
    performed_by VARCHAR(100) NOT NULL,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 10. App-Owned: Transfer confirmations (inter-facility confirmation)
CREATE TABLE IF NOT EXISTS supply_intel.transfer_confirmations (
    confirmation_id SERIAL PRIMARY KEY,
    transfer_id INTEGER NOT NULL,
    decision VARCHAR(20) NOT NULL,                     -- approved, rejected
    actual_qty INTEGER,
    notes TEXT,
    confirmed_by VARCHAR(100) NOT NULL,
    confirmed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 11. App-Owned: Audit log (every operational change captured)
CREATE TABLE IF NOT EXISTS supply_intel.audit_log (
    log_id SERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100) NOT NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id VARCHAR(100),
    details JSONB DEFAULT '{}'::jsonb
);

-- 12. App-Owned: Agent sessions (session state for clinical substitution reasoning)
CREATE TABLE IF NOT EXISTS supply_intel.agent_sessions (
    session_id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    agent_type VARCHAR(50),
    context JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

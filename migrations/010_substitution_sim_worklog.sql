-- Agent tool traces written only on sim-* branches during investigation.

CREATE TABLE IF NOT EXISTS supply_intel.substitution_sim_worklog (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    simulation_id UUID NOT NULL,
    branch_id VARCHAR(63) NOT NULL,
    phase TEXT NOT NULL,
    tool TEXT NOT NULL,
    thought TEXT,
    result TEXT,
    sql_text TEXT,
    row_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS substitution_sim_worklog_sim_idx
    ON supply_intel.substitution_sim_worklog (simulation_id, created_at);

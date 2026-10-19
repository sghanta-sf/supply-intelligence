-- App-owned tables for Lakebase-branch substitution simulations.
-- Synced operational tables stay read-only; the agent writes only here.

CREATE TABLE IF NOT EXISTS supply_intel.formulary (
    therapeutic_class VARCHAR(80) PRIMARY KEY,
    active_item_id VARCHAR(20) NOT NULL,
    active_item_description TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS supply_intel.patient_order_census (
    item_id VARCHAR(20) NOT NULL,
    facility_id VARCHAR(20) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    active_order_count INTEGER NOT NULL DEFAULT 0,
    allergy_flag_count INTEGER NOT NULL DEFAULT 0,
    contraindication_count INTEGER NOT NULL DEFAULT 0,
    avg_daily_doses NUMERIC(10,2) NOT NULL DEFAULT 0,
    PRIMARY KEY (item_id, facility_id)
);

CREATE TABLE IF NOT EXISTS supply_intel.substitution_simulations (
    simulation_id UUID PRIMARY KEY,
    branch_id VARCHAR(63) NOT NULL,
    shortage_item_id VARCHAR(20) NOT NULL,
    alternative_item_id VARCHAR(20) NOT NULL,
    substitution_id INTEGER,
    status VARCHAR(20) NOT NULL DEFAULT 'presented',
    impact JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_by VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    decided_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS supply_intel.substitution_sim_allocations (
    allocation_id SERIAL PRIMARY KEY,
    simulation_id UUID NOT NULL,
    branch_id VARCHAR(63) NOT NULL,
    facility_id VARCHAR(20) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    patients INTEGER NOT NULL,
    units_allocated INTEGER NOT NULL,
    days_cover NUMERIC(8,1) NOT NULL,
    monthly_cost_delta NUMERIC(12,2) NOT NULL,
    lead_time_delta_days INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO supply_intel.formulary (therapeutic_class, active_item_id, active_item_description)
VALUES
    ('surgical_prophylaxis_cephalosporin', 'SKU-PH-101', 'Cefazolin 1g IV Vial'),
    ('vte_anticoagulation', 'SKU-PH-102', 'Heparin Sodium 5,000 USP Units/mL 10mL'),
    ('icu_sedation', 'SKU-PH-103', 'Propofol 10mg/mL 20mL Diprivan Emulsion'),
    ('indwelling_urinary_catheter', 'SKU-SR-201', '14 Fr Hydrophilic Foley Catheter Tray w/ Temp Sensor'),
    ('adult_airway_ett', 'SKU-CC-301', 'Endotracheal Tube 7.5mm Cuffed Murphy Eye'),
    ('vasodilator_infusion', 'SKU-PH-106', 'Nitroglycerin 50mg/250mL in D5W Premix')
ON CONFLICT (therapeutic_class) DO NOTHING;

INSERT INTO supply_intel.patient_order_census
    (item_id, facility_id, facility_name, active_order_count, allergy_flag_count, contraindication_count, avg_daily_doses)
VALUES
    ('SKU-PH-101', 'FAC-01', 'Apex Memorial Hospital', 200, 6, 2, 48.0),
    ('SKU-PH-101', 'FAC-02', 'Apex Children''s Medical Center', 50, 3, 1, 12.0),
    ('SKU-PH-101', 'FAC-03', 'Apex Valley Health', 72, 2, 0, 18.0),
    ('SKU-PH-101', 'FAC-04', 'Apex Ambulatory Surgical', 38, 1, 0, 14.0),
    ('SKU-PH-101', 'FAC-05', 'Apex Northgate Clinic', 16, 0, 0, 4.0),
    ('SKU-PH-101', 'FAC-06', 'Apex Central Distribution Hub', 0, 0, 0, 0.0),
    ('SKU-PH-101', 'FAC-07', 'Apex Westside Specialty', 28, 1, 0, 6.0),
    ('SKU-PH-101', 'FAC-08', 'Apex Crestview Rehab', 22, 1, 1, 5.0),
    ('SKU-PH-102', 'FAC-01', 'Apex Memorial Hospital', 120, 4, 8, 36.0),
    ('SKU-PH-102', 'FAC-02', 'Apex Children''s Medical Center', 44, 2, 3, 10.0),
    ('SKU-PH-102', 'FAC-03', 'Apex Valley Health', 51, 1, 2, 12.0),
    ('SKU-PH-102', 'FAC-04', 'Apex Ambulatory Surgical', 19, 0, 1, 6.0),
    ('SKU-PH-103', 'FAC-01', 'Apex Memorial Hospital', 86, 0, 5, 22.0),
    ('SKU-PH-103', 'FAC-03', 'Apex Valley Health', 41, 0, 2, 11.0)
ON CONFLICT (item_id, facility_id) DO NOTHING;

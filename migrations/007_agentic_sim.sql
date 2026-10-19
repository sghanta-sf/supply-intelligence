-- Patient-level flags for agentic substitution simulation (aggregated cohorts).

CREATE TABLE IF NOT EXISTS supply_intel.drug_knowledge (
    item_id VARCHAR(20) PRIMARY KEY,
    item_description TEXT NOT NULL,
    pharmacologic_class VARCHAR(80) NOT NULL,
    subclass VARCHAR(80),
    pediatric_min_age INTEGER,
    renal_adjustment TEXT,
    dosing_notes TEXT
);

CREATE TABLE IF NOT EXISTS supply_intel.substitution_patient_cohorts (
    cohort_id SERIAL PRIMARY KEY,
    item_id VARCHAR(20) NOT NULL,
    facility_id VARCHAR(20) NOT NULL,
    facility_name VARCHAR(100) NOT NULL,
    indication VARCHAR(80) NOT NULL,
    age_band VARCHAR(20) NOT NULL,
    egfr_band VARCHAR(20) NOT NULL,
    angioedema BOOLEAN NOT NULL DEFAULT FALSE,
    potassium_concurrent BOOLEAN NOT NULL DEFAULT FALSE,
    patient_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS supply_intel.substitution_sim_categories (
    category_id SERIAL PRIMARY KEY,
    simulation_id UUID NOT NULL,
    branch_id VARCHAR(63) NOT NULL,
    category_key VARCHAR(8) NOT NULL,
    label TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL,
    patient_count INTEGER NOT NULL,
    recommendation TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO supply_intel.drug_knowledge
    (item_id, item_description, pharmacologic_class, subclass, pediatric_min_age, renal_adjustment, dosing_notes)
VALUES
    ('SKU-PH-101', 'Cefazolin 1g IV Vial', 'cephalosporin', '1st generation', 0, 'renal dose adjust CrCl < 30', 'Surgical prophylaxis; not a class switch when using cefuroxime.'),
    ('SKU-PH-ALT-02', 'Cefuroxime 1.5g IV Vial (Zinacef)', 'cephalosporin', '2nd generation', 3, 'renal dose adjust CrCl < 30', 'Equivalent prophylaxis coverage for most adult surgical indications.'),
    ('SKU-PH-112', 'Lisinopril 10mg Tablet', 'ACE inhibitor', 'ACE-I', 6, 'use caution eGFR < 30; start low', 'Hypertension 10mg; HFrEF / post-MI often titrated. ACE-I angioedema risk.'),
    ('SKU-PH-ALT-20', 'Losartan 50mg Tablet', 'ARB', 'angiotensin receptor blocker', 6, 'consider 25mg start if eGFR < 30', 'HTN often 50mg; HFrEF start 25mg and titrate. Lower angioedema risk; 2-8% ACE-I cross-reactivity.'),
    ('SKU-PH-ALT-21', 'Amlodipine 2.5mg Tablet', 'calcium channel blocker', 'dihydropyridine', 6, 'none typical', 'Pediatric hypertension alternative when ARB/ACE-I not suitable.')
ON CONFLICT (item_id) DO NOTHING;

INSERT INTO supply_intel.formulary (therapeutic_class, active_item_id, active_item_description)
VALUES ('hypertension_ace_inhibitor', 'SKU-PH-112', 'Lisinopril 10mg Tablet')
ON CONFLICT (therapeutic_class) DO NOTHING;

INSERT INTO supply_intel.substitution_candidates
    (shortage_item_id, shortage_item_description, alternative_item_id, alternative_item_description,
     clinical_equivalence, formulary_status, availability, agent_reasoning, confidence_score)
SELECT 'SKU-PH-112', 'Lisinopril 10mg Tablet', 'SKU-PH-ALT-20', 'Losartan 50mg Tablet',
       'similar', 'on_formulary', 'in_stock',
       'ACE-I to ARB therapeutic class switch. Not a generic swap — screen angioedema, renal function, pediatric label, and indication-based dose equivalency.',
       88.0
WHERE NOT EXISTS (
    SELECT 1 FROM supply_intel.substitution_candidates
    WHERE shortage_item_id = 'SKU-PH-112' AND alternative_item_id = 'SKU-PH-ALT-20'
);

INSERT INTO supply_intel.patient_order_census
    (item_id, facility_id, facility_name, active_order_count, allergy_flag_count, contraindication_count, avg_daily_doses)
VALUES
    ('SKU-PH-112', 'FAC-01', 'Apex Memorial Hospital', 520, 12, 18, 520),
    ('SKU-PH-112', 'FAC-02', 'Apex Children''s Medical Center', 187, 3, 4, 90),
    ('SKU-PH-112', 'FAC-03', 'Apex Valley Health', 310, 4, 8, 310),
    ('SKU-PH-112', 'FAC-04', 'Apex Ambulatory Surgical', 165, 1, 3, 140),
    ('SKU-PH-112', 'FAC-05', 'Apex Northgate Clinic', 98, 1, 2, 98),
    ('SKU-PH-112', 'FAC-07', 'Apex Westside Specialty', 240, 1, 4, 240),
    ('SKU-PH-112', 'FAC-08', 'Apex Crestview Rehab', 327, 1, 2, 327)
ON CONFLICT (item_id, facility_id) DO NOTHING;

INSERT INTO supply_intel.substitution_patient_cohorts
    (item_id, facility_id, facility_name, indication, age_band, egfr_band, angioedema, potassium_concurrent, patient_count)
VALUES
    ('SKU-PH-112', 'FAC-01', 'Apex Memorial Hospital', 'hypertension', 'adult', 'ge30', FALSE, FALSE, 268),
    ('SKU-PH-112', 'FAC-01', 'Apex Memorial Hospital', 'hypertension', 'adult', 'ge30', FALSE, TRUE, 110),
    ('SKU-PH-112', 'FAC-01', 'Apex Memorial Hospital', 'heart_failure_post_mi', 'adult', 'ge30', FALSE, FALSE, 102),
    ('SKU-PH-112', 'FAC-01', 'Apex Memorial Hospital', 'heart_failure_post_mi', 'adult', 'lt30', FALSE, TRUE, 18),
    ('SKU-PH-112', 'FAC-01', 'Apex Memorial Hospital', 'hypertension', 'adult', 'ge30', TRUE, FALSE, 12),
    ('SKU-PH-112', 'FAC-01', 'Apex Memorial Hospital', 'hypertension', 'adult', 'lt30', FALSE, FALSE, 10),
    ('SKU-PH-112', 'FAC-02', 'Apex Children''s Medical Center', 'hypertension', 'pediatric_6_17', 'ge30', FALSE, FALSE, 148),
    ('SKU-PH-112', 'FAC-02', 'Apex Children''s Medical Center', 'hypertension', 'pediatric_lt6', 'ge30', FALSE, FALSE, 2),
    ('SKU-PH-112', 'FAC-02', 'Apex Children''s Medical Center', 'hypertension', 'pediatric_6_17', 'ge30', TRUE, FALSE, 3),
    ('SKU-PH-112', 'FAC-02', 'Apex Children''s Medical Center', 'hypertension', 'pediatric_6_17', 'lt30', FALSE, TRUE, 4),
    ('SKU-PH-112', 'FAC-02', 'Apex Children''s Medical Center', 'hypertension', 'pediatric_6_17', 'ge30', FALSE, TRUE, 30),
    ('SKU-PH-112', 'FAC-03', 'Apex Valley Health', 'hypertension', 'adult', 'ge30', FALSE, FALSE, 160),
    ('SKU-PH-112', 'FAC-03', 'Apex Valley Health', 'hypertension', 'adult', 'ge30', FALSE, TRUE, 70),
    ('SKU-PH-112', 'FAC-03', 'Apex Valley Health', 'heart_failure_post_mi', 'adult', 'ge30', FALSE, FALSE, 68),
    ('SKU-PH-112', 'FAC-03', 'Apex Valley Health', 'hypertension', 'adult', 'ge30', TRUE, FALSE, 4),
    ('SKU-PH-112', 'FAC-03', 'Apex Valley Health', 'heart_failure_post_mi', 'adult', 'lt30', FALSE, FALSE, 8),
    ('SKU-PH-112', 'FAC-04', 'Apex Ambulatory Surgical', 'hypertension', 'adult', 'ge30', FALSE, FALSE, 120),
    ('SKU-PH-112', 'FAC-04', 'Apex Ambulatory Surgical', 'hypertension', 'adult', 'ge30', FALSE, TRUE, 40),
    ('SKU-PH-112', 'FAC-04', 'Apex Ambulatory Surgical', 'hypertension', 'adult', 'ge30', TRUE, FALSE, 1),
    ('SKU-PH-112', 'FAC-04', 'Apex Ambulatory Surgical', 'hypertension', 'adult', 'lt30', FALSE, FALSE, 4),
    ('SKU-PH-112', 'FAC-05', 'Apex Northgate Clinic', 'hypertension', 'adult', 'ge30', FALSE, FALSE, 72),
    ('SKU-PH-112', 'FAC-05', 'Apex Northgate Clinic', 'hypertension', 'adult', 'ge30', FALSE, TRUE, 22),
    ('SKU-PH-112', 'FAC-05', 'Apex Northgate Clinic', 'hypertension', 'adult', 'ge30', TRUE, FALSE, 1),
    ('SKU-PH-112', 'FAC-05', 'Apex Northgate Clinic', 'hypertension', 'adult', 'lt30', FALSE, FALSE, 3),
    ('SKU-PH-112', 'FAC-07', 'Apex Westside Specialty', 'hypertension', 'adult', 'ge30', FALSE, FALSE, 130),
    ('SKU-PH-112', 'FAC-07', 'Apex Westside Specialty', 'heart_failure_post_mi', 'adult', 'ge30', FALSE, FALSE, 85),
    ('SKU-PH-112', 'FAC-07', 'Apex Westside Specialty', 'hypertension', 'adult', 'ge30', FALSE, TRUE, 20),
    ('SKU-PH-112', 'FAC-07', 'Apex Westside Specialty', 'hypertension', 'adult', 'ge30', TRUE, FALSE, 1),
    ('SKU-PH-112', 'FAC-07', 'Apex Westside Specialty', 'heart_failure_post_mi', 'adult', 'lt30', FALSE, FALSE, 4),
    ('SKU-PH-112', 'FAC-08', 'Apex Crestview Rehab', 'hypertension', 'adult', 'ge30', FALSE, FALSE, 180),
    ('SKU-PH-112', 'FAC-08', 'Apex Crestview Rehab', 'heart_failure_post_mi', 'adult', 'ge30', FALSE, FALSE, 126),
    ('SKU-PH-112', 'FAC-08', 'Apex Crestview Rehab', 'hypertension', 'adult', 'ge30', FALSE, TRUE, 16),
    ('SKU-PH-112', 'FAC-08', 'Apex Crestview Rehab', 'hypertension', 'adult', 'ge30', TRUE, FALSE, 2),
    ('SKU-PH-112', 'FAC-08', 'Apex Crestview Rehab', 'heart_failure_post_mi', 'adult', 'lt30', FALSE, FALSE, 3);

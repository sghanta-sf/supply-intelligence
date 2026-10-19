-- Demo Migration: Add Expiration Alerts & Clinical Risk Flagging
-- Used in Track C to demonstrate schema evolution on isolated feature branches

ALTER TABLE supply_intel.inventory_snapshot 
ADD COLUMN IF NOT EXISTS days_until_expiration INTEGER DEFAULT 45;

UPDATE supply_intel.inventory_snapshot
SET days_until_expiration = GREATEST(0, (expiration_date - CURRENT_DATE));

ALTER TABLE supply_intel.risk_scores
ADD COLUMN IF NOT EXISTS requires_cold_chain BOOLEAN DEFAULT FALSE;

UPDATE supply_intel.risk_scores 
SET requires_cold_chain = TRUE 
WHERE item_category = 'Pharmacy' AND (item_description ILIKE '%propofol%' OR item_description ILIKE '%heparin%' OR item_description ILIKE '%epinephrine%');

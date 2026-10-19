-- App-owned comments on a recommended purchase order (pharmacist / materials note).
-- Apply on the feature branch first; the same file applies to production later.

ALTER TABLE supply_intel.recommended_orders
    ADD COLUMN IF NOT EXISTS comments TEXT;

-- Lakebase CDF needs REPLICA IDENTITY FULL. The app role may not own these
-- tables, so skip ALTER when the current user cannot change replica identity.
DO $$
DECLARE
  tbl text;
BEGIN
  FOREACH tbl IN ARRAY ARRAY['order_decisions', 'substitution_selections', 'recall_actions']
  LOOP
    IF EXISTS (
      SELECT 1
      FROM pg_class c
      JOIN pg_namespace n ON n.oid = c.relnamespace
      WHERE n.nspname = 'supply_intel'
        AND c.relname = tbl
        AND pg_has_role(current_user, c.relowner, 'USAGE')
    ) THEN
      EXECUTE format('ALTER TABLE supply_intel.%I REPLICA IDENTITY FULL', tbl);
    END IF;
  END LOOP;
END $$;

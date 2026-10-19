-- Vector search for semantic item catalog similarity
DO $$
BEGIN
    CREATE EXTENSION IF NOT EXISTS vector;
    
    CREATE TABLE IF NOT EXISTS supply_intel.item_embeddings (
        item_id VARCHAR(20) PRIMARY KEY,
        item_description TEXT NOT NULL,
        category VARCHAR(50) NOT NULL,
        embedding vector(1536),
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
EXCEPTION WHEN OTHERS THEN
    -- In environments where vector extension is restricted, create metadata fallback table
    CREATE TABLE IF NOT EXISTS supply_intel.item_embeddings (
        item_id VARCHAR(20) PRIMARY KEY,
        item_description TEXT NOT NULL,
        category VARCHAR(50) NOT NULL,
        embedding_json JSONB DEFAULT '[]'::jsonb,
        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
END $$;

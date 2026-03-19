-- Migration: Add domain_id column to user_concept_status
-- Phase 7.5: Multi-domain learning progress isolation

-- Step 1: Add domain_id column with default value (backward compatible)
ALTER TABLE user_concept_status
  ADD COLUMN IF NOT EXISTS domain_id TEXT NOT NULL DEFAULT 'ai-engineering';

-- Step 2: Drop old primary key and recreate with domain_id
-- The old PK was (user_id, concept_id); new PK is (user_id, concept_id, domain_id)
ALTER TABLE user_concept_status DROP CONSTRAINT IF EXISTS user_concept_status_pkey;
ALTER TABLE user_concept_status ADD PRIMARY KEY (user_id, concept_id, domain_id);

-- Step 3: Index for per-domain queries
CREATE INDEX IF NOT EXISTS idx_user_concept_status_domain
  ON user_concept_status(user_id, domain_id);

-- Step 4: Add domain_id to learning_events if it exists
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'learning_events') THEN
    EXECUTE 'ALTER TABLE learning_events ADD COLUMN IF NOT EXISTS domain_id TEXT NOT NULL DEFAULT ''ai-engineering''';
  END IF;
END $$;

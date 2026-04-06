-- ================================================================
-- Migration: 00003_shared_backend_schemas
-- Description: Multi-project shared backend — schema isolation
-- Date: 2026-04-06
-- Projects: akg, brainforge, newcrpg, timentropy, shared
-- ================================================================

-- ─── Phase 1: Create schemas ───

CREATE SCHEMA IF NOT EXISTS akg;
CREATE SCHEMA IF NOT EXISTS brainforge;
CREATE SCHEMA IF NOT EXISTS newcrpg;
CREATE SCHEMA IF NOT EXISTS timentropy;
CREATE SCHEMA IF NOT EXISTS shared;

-- ─── Phase 1: Grant schema usage ───

GRANT USAGE ON SCHEMA akg TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA brainforge TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA newcrpg TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA timentropy TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA shared TO anon, authenticated, service_role;

-- ─── Phase 1: Default privileges for future tables ───

ALTER DEFAULT PRIVILEGES IN SCHEMA akg
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA akg
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA brainforge
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA brainforge
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA newcrpg
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA newcrpg
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA timentropy
  GRANT SELECT ON TABLES TO anon;
ALTER DEFAULT PRIVILEGES IN SCHEMA timentropy
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA timentropy
  GRANT ALL ON TABLES TO service_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA shared
  GRANT SELECT ON TABLES TO authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA shared
  GRANT ALL ON TABLES TO service_role;

-- ─── Phase 1: Expose schemas to PostgREST ───

ALTER ROLE authenticator SET pgrst.db_schemas TO
  'public, akg, brainforge, newcrpg, timentropy, shared, graphql_public';
NOTIFY pgrst, 'reload schema';

-- ─── Phase 1.2: Shared tables ───

CREATE TABLE shared.user_projects (
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  project     TEXT NOT NULL CHECK (project IN ('akg', 'brainforge', 'newcrpg', 'timentropy')),
  first_seen  TIMESTAMPTZ DEFAULT NOW(),
  last_active TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, project)
);
ALTER TABLE shared.user_projects ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users_own_projects" ON shared.user_projects
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
GRANT SELECT, INSERT, UPDATE ON shared.user_projects TO authenticated;
GRANT ALL ON shared.user_projects TO service_role;

CREATE TABLE shared.feedback (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  project     TEXT NOT NULL,
  category    TEXT DEFAULT 'general',
  content     TEXT NOT NULL,
  metadata    JSONB DEFAULT '{}'::jsonb,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE shared.feedback ENABLE ROW LEVEL SECURITY;
CREATE POLICY "users_insert_feedback" ON shared.feedback
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "users_read_own_feedback" ON shared.feedback
  FOR SELECT USING (auth.uid() = user_id);
GRANT SELECT, INSERT ON shared.feedback TO authenticated;
GRANT ALL ON shared.feedback TO service_role;

-- ─── Phase 2: Migrate AKG tables from public → akg schema ───
-- All tables confirmed empty (0 rows). Safe to move.

ALTER TABLE public.profiles SET SCHEMA akg;
ALTER TABLE public.user_settings SET SCHEMA akg;
ALTER TABLE public.user_concept_status SET SCHEMA akg;
ALTER TABLE public.conversations SET SCHEMA akg;
ALTER TABLE public.learning_events SET SCHEMA akg;

GRANT SELECT, INSERT, UPDATE ON akg.profiles TO authenticated;
GRANT ALL ON akg.profiles TO service_role;
GRANT SELECT, INSERT, UPDATE ON akg.user_settings TO authenticated;
GRANT ALL ON akg.user_settings TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON akg.user_concept_status TO authenticated;
GRANT ALL ON akg.user_concept_status TO service_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON akg.conversations TO authenticated;
GRANT ALL ON akg.conversations TO service_role;
GRANT SELECT, INSERT ON akg.learning_events TO authenticated;
GRANT ALL ON akg.learning_events TO service_role;

-- ─── Phase 2b: Replace trigger, add lazy profile creation ───

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS public.handle_new_user();

CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER LANGUAGE plpgsql SECURITY DEFINER SET search_path = public AS $$
BEGIN
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

CREATE OR REPLACE FUNCTION akg.ensure_profile()
RETURNS UUID LANGUAGE plpgsql SECURITY DEFINER SET search_path = akg, shared AS $$
DECLARE
  _uid UUID := auth.uid();
  _email TEXT;
BEGIN
  IF EXISTS (SELECT 1 FROM akg.profiles WHERE id = _uid) THEN
    RETURN _uid;
  END IF;
  SELECT email INTO _email FROM auth.users WHERE id = _uid;
  INSERT INTO akg.profiles (id, email, display_name)
  VALUES (_uid, _email, split_part(_email, '@', 1));
  INSERT INTO akg.user_settings (user_id) VALUES (_uid);
  INSERT INTO shared.user_projects (user_id, project)
  VALUES (_uid, 'akg') ON CONFLICT DO NOTHING;
  RETURN _uid;
END;
$$;
GRANT EXECUTE ON FUNCTION akg.ensure_profile() TO authenticated;

-- ─── Phase 3: BrainForge schema ───

CREATE TABLE brainforge.user_profiles (
  user_id         UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name    TEXT,
  birth_year      SMALLINT CHECK (birth_year BETWEEN 1940 AND 2010),
  education_level TEXT CHECK (education_level IN (
    'high_school', 'some_college', 'bachelors', 'masters', 'doctorate', 'other'
  )),
  timezone        TEXT DEFAULT 'UTC',
  subscription    TEXT NOT NULL DEFAULT 'free' CHECK (subscription IN ('free', 'premium')),
  onboarding_done BOOLEAN NOT NULL DEFAULT false,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
ALTER TABLE brainforge.user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_profile" ON brainforge.user_profiles
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
GRANT SELECT, INSERT, UPDATE ON brainforge.user_profiles TO authenticated;
GRANT ALL ON brainforge.user_profiles TO service_role;

CREATE TABLE brainforge.training_sessions (
  session_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  task_type        TEXT NOT NULL,
  started_at       TIMESTAMPTZ NOT NULL,
  completed_at     TIMESTAMPTZ,
  duration_seconds INTEGER GENERATED ALWAYS AS (
    EXTRACT(EPOCH FROM (completed_at - started_at))::INTEGER
  ) STORED,
  final_level      SMALLINT NOT NULL DEFAULT 1 CHECK (final_level >= 1),
  overall_accuracy REAL CHECK (overall_accuracy BETWEEN 0 AND 1),
  client_session_id TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_bf_sessions_user_task
  ON brainforge.training_sessions (user_id, task_type, started_at DESC);
CREATE INDEX idx_bf_sessions_client_id
  ON brainforge.training_sessions (client_session_id) WHERE client_session_id IS NOT NULL;
ALTER TABLE brainforge.training_sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_sessions" ON brainforge.training_sessions
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
GRANT SELECT, INSERT, UPDATE, DELETE ON brainforge.training_sessions TO authenticated;
GRANT ALL ON brainforge.training_sessions TO service_role;

CREATE TABLE brainforge.trial_results (
  id               BIGSERIAL PRIMARY KEY,
  session_id       UUID NOT NULL REFERENCES brainforge.training_sessions(session_id) ON DELETE CASCADE,
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  task_type        TEXT NOT NULL,
  block_index      SMALLINT NOT NULL,
  trial_index      SMALLINT NOT NULL,
  difficulty       SMALLINT NOT NULL CHECK (difficulty >= 1),
  is_correct       BOOLEAN NOT NULL,
  reaction_time_ms INTEGER NOT NULL,
  metadata         JSONB DEFAULT '{}'::jsonb,
  recorded_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_bf_trials_session
  ON brainforge.trial_results (session_id, block_index, trial_index);
CREATE INDEX idx_bf_trials_user_task
  ON brainforge.trial_results (user_id, task_type, recorded_at DESC);
ALTER TABLE brainforge.trial_results ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_trials" ON brainforge.trial_results
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
GRANT SELECT, INSERT ON brainforge.trial_results TO authenticated;
GRANT ALL ON brainforge.trial_results TO service_role;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA brainforge TO authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA brainforge TO service_role;

CREATE TABLE brainforge.daily_checkins (
  user_id        UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  checkin_date   DATE NOT NULL,
  sessions_count SMALLINT NOT NULL DEFAULT 0,
  total_time_sec INTEGER NOT NULL DEFAULT 0,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (user_id, checkin_date)
);
ALTER TABLE brainforge.daily_checkins ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_checkins" ON brainforge.daily_checkins
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
GRANT SELECT, INSERT, UPDATE ON brainforge.daily_checkins TO authenticated;
GRANT ALL ON brainforge.daily_checkins TO service_role;

CREATE TABLE brainforge.assessments (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  assessment_type  TEXT NOT NULL CHECK (assessment_type IN ('baseline', 'retest_4w', 'retest_8w', 'retest_12w')),
  results          JSONB NOT NULL DEFAULT '{}'::jsonb,
  composite_score  REAL,
  started_at       TIMESTAMPTZ NOT NULL,
  completed_at     TIMESTAMPTZ,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_bf_assessments_user
  ON brainforge.assessments (user_id, assessment_type, created_at DESC);
ALTER TABLE brainforge.assessments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "own_assessments" ON brainforge.assessments
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
GRANT SELECT, INSERT ON brainforge.assessments TO authenticated;
GRANT ALL ON brainforge.assessments TO service_role;

CREATE OR REPLACE FUNCTION brainforge.ensure_profile()
RETURNS UUID LANGUAGE plpgsql SECURITY DEFINER SET search_path = brainforge, shared AS $$
DECLARE
  _uid UUID := auth.uid();
BEGIN
  IF EXISTS (SELECT 1 FROM brainforge.user_profiles WHERE user_id = _uid) THEN
    RETURN _uid;
  END IF;
  INSERT INTO brainforge.user_profiles (user_id) VALUES (_uid);
  INSERT INTO shared.user_projects (user_id, project)
  VALUES (_uid, 'brainforge') ON CONFLICT DO NOTHING;
  RETURN _uid;
END;
$$;
GRANT EXECUTE ON FUNCTION brainforge.ensure_profile() TO authenticated;

-- ─── Phase 4: NewCRPG + Timentropy stubs ───

CREATE TABLE newcrpg.shared_worlds (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creator_id  UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  world_seed  JSONB NOT NULL,
  title       TEXT NOT NULL,
  description TEXT,
  plays       INTEGER DEFAULT 0,
  likes       INTEGER DEFAULT 0,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
ALTER TABLE newcrpg.shared_worlds ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anyone_read_worlds" ON newcrpg.shared_worlds FOR SELECT USING (true);
CREATE POLICY "creator_manage_worlds" ON newcrpg.shared_worlds
  FOR ALL USING (auth.uid() = creator_id) WITH CHECK (auth.uid() = creator_id);
GRANT SELECT ON newcrpg.shared_worlds TO anon;
GRANT SELECT, INSERT, UPDATE, DELETE ON newcrpg.shared_worlds TO authenticated;
GRANT ALL ON newcrpg.shared_worlds TO service_role;

CREATE TABLE timentropy.comments (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  article_id  TEXT NOT NULL,
  content     TEXT NOT NULL CHECK (length(content) <= 2000),
  parent_id   UUID REFERENCES timentropy.comments(id) ON DELETE CASCADE,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_tim_comments_article ON timentropy.comments(article_id, created_at);
ALTER TABLE timentropy.comments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anyone_read_comments" ON timentropy.comments FOR SELECT USING (true);
CREATE POLICY "users_create_comments" ON timentropy.comments
  FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "users_delete_own" ON timentropy.comments FOR DELETE USING (auth.uid() = user_id);
GRANT SELECT ON timentropy.comments TO anon;
GRANT SELECT, INSERT, DELETE ON timentropy.comments TO authenticated;
GRANT ALL ON timentropy.comments TO service_role;

CREATE TABLE timentropy.reactions (
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  article_id  TEXT NOT NULL,
  type        TEXT NOT NULL CHECK (type IN ('like', 'bookmark', 'insightful')),
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, article_id, type)
);
ALTER TABLE timentropy.reactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "anyone_read_reactions" ON timentropy.reactions FOR SELECT USING (true);
CREATE POLICY "users_manage_own" ON timentropy.reactions
  FOR ALL USING (auth.uid() = user_id) WITH CHECK (auth.uid() = user_id);
GRANT SELECT ON timentropy.reactions TO anon;
GRANT SELECT, INSERT, DELETE ON timentropy.reactions TO authenticated;
GRANT ALL ON timentropy.reactions TO service_role;

-- ================================================================
-- AKG Supabase 修复脚本 — 合并 migration 00001 + 00002
-- 幂等安全：可重复执行，已存在的对象不会报错
-- 
-- 使用方法：
--   1. 打开 https://supabase.com/dashboard/project/oepkmybgwptxnkpgrglv/sql/new
--   2. 粘贴全部内容
--   3. 点击 Run
-- ================================================================

-- ============================
-- Part 1: 表结构 (00001)
-- ============================

-- 用户资料 (扩展 auth.users)
CREATE TABLE IF NOT EXISTS profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT NOT NULL,
  display_name TEXT NOT NULL DEFAULT '',
  avatar_url  TEXT,
  preferred_language TEXT DEFAULT 'zh-CN',
  study_goal  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 用户设置
CREATE TABLE IF NOT EXISTS user_settings (
  user_id               UUID PRIMARY KEY REFERENCES profiles(id) ON DELETE CASCADE,
  theme                 TEXT DEFAULT 'dark' CHECK (theme IN ('light', 'dark', 'system')),
  daily_goal_minutes    INT DEFAULT 30,
  notification_enabled  BOOLEAN DEFAULT TRUE,
  review_reminder       BOOLEAN DEFAULT TRUE,
  preferred_difficulty  TEXT DEFAULT 'adaptive' CHECK (preferred_difficulty IN ('easy', 'medium', 'hard', 'adaptive'))
);

-- 用户概念学习状态
CREATE TABLE IF NOT EXISTS user_concept_status (
  user_id           UUID REFERENCES profiles(id) ON DELETE CASCADE,
  concept_id        TEXT NOT NULL,
  status            TEXT NOT NULL DEFAULT 'locked' CHECK (status IN ('locked', 'available', 'learning', 'reviewing', 'mastered')),
  mastery_level     FLOAT DEFAULT 0 CHECK (mastery_level >= 0 AND mastery_level <= 1),
  fsrs_stability    FLOAT,
  fsrs_difficulty   FLOAT,
  fsrs_due_date     TIMESTAMPTZ,
  fsrs_last_review  TIMESTAMPTZ,
  total_sessions    INT DEFAULT 0,
  total_time_sec    INT DEFAULT 0,
  feynman_score     FLOAT,
  last_feynman_at   TIMESTAMPTZ,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (user_id, concept_id)
);

-- 对话历史
CREATE TABLE IF NOT EXISTS conversations (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID REFERENCES profiles(id) ON DELETE CASCADE,
  concept_id            TEXT NOT NULL,
  messages              JSONB DEFAULT '[]'::JSONB,
  summary               TEXT,
  understanding_delta   FLOAT,
  status                TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'abandoned')),
  created_at            TIMESTAMPTZ DEFAULT NOW(),
  updated_at            TIMESTAMPTZ DEFAULT NOW()
);

-- 学习事件流
CREATE TABLE IF NOT EXISTS learning_events (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID REFERENCES profiles(id) ON DELETE CASCADE,
  concept_id  TEXT NOT NULL,
  event_type  TEXT NOT NULL CHECK (event_type IN ('feynman_attempt', 'review', 'quiz', 'unlock', 'mastered')),
  payload     JSONB DEFAULT '{}'::JSONB,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_user_concept_status_user ON user_concept_status(user_id);
CREATE INDEX IF NOT EXISTS idx_user_concept_status_concept ON user_concept_status(concept_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_concept ON conversations(concept_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_user ON learning_events(user_id);
CREATE INDEX IF NOT EXISTS idx_learning_events_type ON learning_events(event_type);

-- ============================
-- Part 2: RLS 策略 (幂等)
-- ============================

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_concept_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_events ENABLE ROW LEVEL SECURITY;

-- 先删再建，保证幂等
DROP POLICY IF EXISTS "Users can read own profile" ON profiles;
CREATE POLICY "Users can read own profile" ON profiles FOR SELECT USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON profiles;
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can read own settings" ON user_settings;
CREATE POLICY "Users can read own settings" ON user_settings FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can upsert own settings" ON user_settings;
CREATE POLICY "Users can upsert own settings" ON user_settings FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can read own concept status" ON user_concept_status;
CREATE POLICY "Users can read own concept status" ON user_concept_status FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can upsert own concept status" ON user_concept_status;
CREATE POLICY "Users can upsert own concept status" ON user_concept_status FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can read own conversations" ON conversations;
CREATE POLICY "Users can read own conversations" ON conversations FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own conversations" ON conversations;
CREATE POLICY "Users can manage own conversations" ON conversations FOR ALL USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can read own events" ON learning_events;
CREATE POLICY "Users can read own events" ON learning_events FOR SELECT USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own events" ON learning_events;
CREATE POLICY "Users can insert own events" ON learning_events FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================
-- Part 3: 触发器 — 新用户自动创建 profile
-- ============================

CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $trigger$
BEGIN
  INSERT INTO profiles (id, email, display_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'display_name', split_part(NEW.email, '@', 1))
  );
  INSERT INTO user_settings (user_id) VALUES (NEW.id);
  RETURN NEW;
END;
$trigger$ LANGUAGE plpgsql SECURITY DEFINER;

DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- ============================
-- Part 4: PostgREST 权限
-- ============================

GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;

GRANT SELECT ON profiles TO authenticated;
GRANT ALL ON profiles TO service_role;
GRANT INSERT, UPDATE ON profiles TO authenticated;

GRANT SELECT ON user_settings TO authenticated;
GRANT ALL ON user_settings TO service_role;
GRANT INSERT, UPDATE ON user_settings TO authenticated;

GRANT SELECT ON user_concept_status TO authenticated;
GRANT ALL ON user_concept_status TO service_role;
GRANT INSERT, UPDATE, DELETE ON user_concept_status TO authenticated;

GRANT SELECT ON conversations TO authenticated;
GRANT ALL ON conversations TO service_role;
GRANT INSERT, UPDATE, DELETE ON conversations TO authenticated;

GRANT SELECT ON learning_events TO authenticated;
GRANT ALL ON learning_events TO service_role;
GRANT INSERT ON learning_events TO authenticated;

-- ============================
-- Part 5: Migration 00002 — domain_id
-- ============================

ALTER TABLE user_concept_status
  ADD COLUMN IF NOT EXISTS domain_id TEXT NOT NULL DEFAULT 'ai-engineering';

-- 重建主键（如果已经是三列主键则跳过）
DO $do$
BEGIN
  -- 检查当前主键列数，如果只有2列则需要重建
  IF (SELECT count(*) FROM information_schema.key_column_usage 
      WHERE constraint_name = 'user_concept_status_pkey' 
      AND table_name = 'user_concept_status') < 3 THEN
    ALTER TABLE user_concept_status DROP CONSTRAINT IF EXISTS user_concept_status_pkey;
    ALTER TABLE user_concept_status ADD PRIMARY KEY (user_id, concept_id, domain_id);
  END IF;
END $do$;

CREATE INDEX IF NOT EXISTS idx_user_concept_status_domain
  ON user_concept_status(user_id, domain_id);

DO $do2$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'learning_events') THEN
    EXECUTE 'ALTER TABLE learning_events ADD COLUMN IF NOT EXISTS domain_id TEXT NOT NULL DEFAULT ''ai-engineering''';
  END IF;
END $do2$;

-- ============================
-- 验证
-- ============================
SELECT 'Migration complete!' AS status, 
       (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('profiles', 'user_settings', 'user_concept_status', 'conversations', 'learning_events')) AS tables_created,
       (SELECT count(*) FROM pg_trigger WHERE tgname = 'on_auth_user_created') AS trigger_exists;

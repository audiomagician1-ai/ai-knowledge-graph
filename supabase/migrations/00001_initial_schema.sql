-- ========================================
-- AI Knowledge Graph — Initial Schema
-- 用户资料 + 学习状态 + 对话 + 事件
-- ========================================

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
  -- FSRS 字段
  fsrs_stability    FLOAT,
  fsrs_difficulty   FLOAT,
  fsrs_due_date     TIMESTAMPTZ,
  fsrs_last_review  TIMESTAMPTZ,
  -- 统计
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

-- RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_concept_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE learning_events ENABLE ROW LEVEL SECURITY;

-- Profiles: 自己可读写
CREATE POLICY "Users can read own profile" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON profiles FOR UPDATE USING (auth.uid() = id);

-- Settings: 自己可读写
CREATE POLICY "Users can read own settings" ON user_settings FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can upsert own settings" ON user_settings FOR ALL USING (auth.uid() = user_id);

-- Concept status: 自己可读写
CREATE POLICY "Users can read own concept status" ON user_concept_status FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can upsert own concept status" ON user_concept_status FOR ALL USING (auth.uid() = user_id);

-- Conversations: 自己可读写
CREATE POLICY "Users can read own conversations" ON conversations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can manage own conversations" ON conversations FOR ALL USING (auth.uid() = user_id);

-- Learning events: 自己可读，系统可写
CREATE POLICY "Users can read own events" ON learning_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own events" ON learning_events FOR INSERT WITH CHECK (auth.uid() = user_id);

-- 自动创建 profile 的触发器
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
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
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE OR REPLACE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- PostgREST 角色权限 (Supabase REST API 必需)
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

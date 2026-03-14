-- AI Knowledge Graph — D1 Schema
-- Learning progress + conversation history

CREATE TABLE IF NOT EXISTS concept_progress (
  concept_id TEXT PRIMARY KEY,
  status TEXT NOT NULL DEFAULT 'not_started',
  mastery_score REAL NOT NULL DEFAULT 0,
  last_score REAL,
  sessions INTEGER NOT NULL DEFAULT 0,
  total_time_sec INTEGER NOT NULL DEFAULT 0,
  mastered_at REAL,
  last_learn_at REAL,
  created_at REAL NOT NULL DEFAULT (unixepoch()),
  updated_at REAL NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS learning_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  concept_id TEXT NOT NULL,
  concept_name TEXT NOT NULL,
  score REAL NOT NULL DEFAULT 0,
  mastered INTEGER NOT NULL DEFAULT 0,
  timestamp REAL NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS conversations (
  id TEXT PRIMARY KEY,
  concept_id TEXT NOT NULL,
  concept_name TEXT NOT NULL DEFAULT '',
  system_prompt TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'active',
  is_milestone INTEGER NOT NULL DEFAULT 0,
  created_at REAL NOT NULL DEFAULT (unixepoch()),
  updated_at REAL NOT NULL DEFAULT (unixepoch())
);

CREATE TABLE IF NOT EXISTS messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT NOT NULL,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at REAL NOT NULL DEFAULT (unixepoch()),
  FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE IF NOT EXISTS streak (
  id INTEGER PRIMARY KEY DEFAULT 1,
  current_streak INTEGER NOT NULL DEFAULT 0,
  longest_streak INTEGER NOT NULL DEFAULT 0,
  last_date TEXT NOT NULL DEFAULT ''
);

-- Initialize streak row
INSERT OR IGNORE INTO streak (id, current_streak, longest_streak, last_date) VALUES (1, 0, 0, '');

-- Indexes
CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_history_concept ON learning_history(concept_id);
CREATE INDEX IF NOT EXISTS idx_history_ts ON learning_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_concept ON conversations(concept_id);

"""
SQLite 持久化层 — 本地学习数据 + 对话历史
适配 PyInstaller EXE 单文件模式: 数据库文件存放在 exe 同目录的 data/ 下

表结构:
  - concept_progress: 每个概念的学习状态 (status/score/sessions/timestamps)
  - learning_history: 学习记录流水 (concept/score/mastered/timestamp)
  - conversations: 对话会话元数据
  - messages: 对话消息
  - streak: 连续学习天数
"""

import json
import os
import sqlite3
import sys
import time
import logging
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

logger = logging.getLogger(__name__)

# ── DB file location ──
# In frozen mode (EXE): next to the exe file
# In dev mode: project root / data /
if getattr(sys, 'frozen', False):
    _DB_DIR = Path(sys.executable).parent / "data"
else:
    _DB_DIR = Path(__file__).parent.parent.parent.parent / "data"

_DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = _DB_DIR / "akg_local.db"

_SCHEMA_VERSION = 1


def _get_conn() -> sqlite3.Connection:
    """Create a new connection with WAL mode and foreign keys."""
    conn = sqlite3.connect(str(DB_PATH), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = _get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Initialize the database schema (idempotent)."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY
            );

            -- Concept learning progress
            CREATE TABLE IF NOT EXISTS concept_progress (
                concept_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'not_started',
                mastery_score REAL NOT NULL DEFAULT 0,
                last_score REAL,
                sessions INTEGER NOT NULL DEFAULT 0,
                total_time_sec REAL NOT NULL DEFAULT 0,
                mastered_at REAL,
                last_learn_at REAL,
                created_at REAL NOT NULL DEFAULT (strftime('%s','now')),
                updated_at REAL NOT NULL DEFAULT (strftime('%s','now'))
            );

            -- Learning history log
            CREATE TABLE IF NOT EXISTS learning_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id TEXT NOT NULL,
                concept_name TEXT NOT NULL,
                score REAL NOT NULL,
                mastered INTEGER NOT NULL DEFAULT 0,
                timestamp REAL NOT NULL,
                created_at REAL NOT NULL DEFAULT (strftime('%s','now'))
            );
            CREATE INDEX IF NOT EXISTS idx_history_ts ON learning_history(timestamp DESC);

            -- Streak tracking
            CREATE TABLE IF NOT EXISTS streak (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                current_streak INTEGER NOT NULL DEFAULT 0,
                longest_streak INTEGER NOT NULL DEFAULT 0,
                last_date TEXT NOT NULL DEFAULT ''
            );

            -- Conversations
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                concept_id TEXT NOT NULL,
                concept_name TEXT NOT NULL,
                system_prompt TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active',
                is_milestone INTEGER NOT NULL DEFAULT 0,
                last_active REAL NOT NULL,
                created_at REAL NOT NULL DEFAULT (strftime('%s','now'))
            );
            CREATE INDEX IF NOT EXISTS idx_conv_active ON conversations(last_active DESC);

            -- Messages
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                created_at REAL NOT NULL DEFAULT (strftime('%s','now'))
            );
            CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages(conversation_id, id);

            -- Initialize streak row if not exists
            INSERT OR IGNORE INTO streak (id, current_streak, longest_streak, last_date) VALUES (1, 0, 0, '');

            -- Initialize schema version
            INSERT OR IGNORE INTO schema_version (version) VALUES (1);
        """)

    logger.info("SQLite DB initialized at %s", DB_PATH)


# ════════════════════════════════════════════
# Concept Progress CRUD
# ════════════════════════════════════════════

def get_all_progress() -> list[dict]:
    """Get all concept progress records."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM concept_progress").fetchall()
        return [dict(r) for r in rows]


def get_progress(concept_id: str) -> Optional[dict]:
    """Get progress for a single concept."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM concept_progress WHERE concept_id = ?", (concept_id,)).fetchone()
        return dict(row) if row else None


def upsert_progress(concept_id: str, **kwargs) -> dict:
    """Insert or update concept progress."""
    now = time.time()
    existing = get_progress(concept_id)

    with get_db() as conn:
        if existing:
            fields = []
            values = []
            for k, v in kwargs.items():
                if k in ('status', 'mastery_score', 'last_score', 'sessions', 'total_time_sec', 'mastered_at', 'last_learn_at'):
                    fields.append(f"{k} = ?")
                    values.append(v)
            fields.append("updated_at = ?")
            values.append(now)
            values.append(concept_id)
            conn.execute(f"UPDATE concept_progress SET {', '.join(fields)} WHERE concept_id = ?", values)
        else:
            cols = ['concept_id', 'status', 'mastery_score', 'sessions', 'total_time_sec', 'last_learn_at', 'created_at', 'updated_at']
            vals = [
                concept_id,
                kwargs.get('status', 'not_started'),
                kwargs.get('mastery_score', 0),
                kwargs.get('sessions', 0),
                kwargs.get('total_time_sec', 0),
                kwargs.get('last_learn_at', now),
                now, now,
            ]
            for extra in ('last_score', 'mastered_at'):
                if extra in kwargs:
                    cols.append(extra)
                    vals.append(kwargs[extra])
            placeholders = ', '.join('?' * len(cols))
            conn.execute(f"INSERT INTO concept_progress ({', '.join(cols)}) VALUES ({placeholders})", vals)

    return get_progress(concept_id) or {}


def start_learning(concept_id: str) -> dict:
    """Mark concept as learning, increment session count."""
    now = time.time()
    existing = get_progress(concept_id)
    if existing:
        new_status = 'mastered' if existing['status'] == 'mastered' else 'learning'
        return upsert_progress(
            concept_id,
            status=new_status,
            sessions=existing['sessions'] + 1,
            last_learn_at=now,
        )
    else:
        return upsert_progress(
            concept_id,
            status='learning',
            mastery_score=0,
            sessions=1,
            last_learn_at=now,
        )


def record_assessment(concept_id: str, concept_name: str, score: float, mastered: bool) -> dict:
    """Record assessment result, potentially marking as mastered."""
    now = time.time()
    existing = get_progress(concept_id)
    old_score = existing['mastery_score'] if existing else 0

    progress = upsert_progress(
        concept_id,
        status='mastered' if mastered else 'learning',
        mastery_score=max(score, old_score) if mastered else score,
        last_score=score,
        sessions=max((existing['sessions'] if existing else 0), 1),
        mastered_at=now if mastered and not (existing and existing.get('mastered_at')) else (existing.get('mastered_at') if existing else None),
        last_learn_at=now,
    )

    # Add to history
    add_history(concept_id, concept_name, score, mastered, now)
    # Update streak
    update_streak()

    return progress


# ════════════════════════════════════════════
# Learning History
# ════════════════════════════════════════════

def add_history(concept_id: str, concept_name: str, score: float, mastered: bool, timestamp: float = None):
    """Add a learning history entry."""
    ts = timestamp or time.time()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO learning_history (concept_id, concept_name, score, mastered, timestamp) VALUES (?, ?, ?, ?, ?)",
            (concept_id, concept_name, score, 1 if mastered else 0, ts),
        )


def get_history(limit: int = 100) -> list[dict]:
    """Get recent learning history."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM learning_history ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ════════════════════════════════════════════
# Streak
# ════════════════════════════════════════════

def _today_str() -> str:
    from datetime import date
    return date.today().isoformat()


def _yesterday_str() -> str:
    from datetime import date, timedelta
    return (date.today() - timedelta(days=1)).isoformat()


def get_streak() -> dict:
    """Get current streak data."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM streak WHERE id = 1").fetchone()
        if row:
            return dict(row)
        return {'current_streak': 0, 'longest_streak': 0, 'last_date': ''}


def update_streak() -> dict:
    """Update streak for today's learning activity."""
    streak = get_streak()
    today = _today_str()

    if streak['last_date'] == today:
        return streak  # Already counted today

    if streak['last_date'] == _yesterday_str():
        new_current = streak['current_streak'] + 1
    else:
        new_current = 1

    new_longest = max(streak['longest_streak'], new_current)

    with get_db() as conn:
        conn.execute(
            "UPDATE streak SET current_streak = ?, longest_streak = ?, last_date = ? WHERE id = 1",
            (new_current, new_longest, today),
        )
    return {'id': 1, 'current_streak': new_current, 'longest_streak': new_longest, 'last_date': today}


def refresh_streak() -> dict:
    """Check and potentially reset streak if it's broken."""
    streak = get_streak()
    today = _today_str()

    if streak['last_date'] and streak['last_date'] != today and streak['last_date'] != _yesterday_str():
        # Streak broken
        with get_db() as conn:
            conn.execute("UPDATE streak SET current_streak = 0 WHERE id = 1")
        streak['current_streak'] = 0

    return streak


# ════════════════════════════════════════════
# Conversations & Messages
# ════════════════════════════════════════════

def save_conversation(conv_id: str, concept_id: str, concept_name: str,
                      system_prompt: str, is_milestone: bool = False) -> dict:
    """Create or update a conversation record."""
    now = time.time()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO conversations (id, concept_id, concept_name, system_prompt, is_milestone, last_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET last_active = ?, status = 'active'
        """, (conv_id, concept_id, concept_name, system_prompt, 1 if is_milestone else 0, now, now, now))
    return {'id': conv_id, 'concept_id': concept_id, 'concept_name': concept_name}


def save_message(conversation_id: str, role: str, content: str, timestamp: float = None):
    """Save a message to the database."""
    ts = timestamp or time.time()
    with get_db() as conn:
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (conversation_id, role, content, ts),
        )


def get_conversation(conv_id: str) -> Optional[dict]:
    """Get conversation with its messages."""
    with get_db() as conn:
        conv = conn.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
        if not conv:
            return None
        messages = conn.execute(
            "SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id",
            (conv_id,)
        ).fetchall()
        result = dict(conv)
        result['messages'] = [dict(m) for m in messages]
        return result


def get_conversation_messages(conv_id: str) -> list[dict]:
    """Get messages for a conversation."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, timestamp FROM messages WHERE conversation_id = ? ORDER BY id",
            (conv_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def update_conversation_status(conv_id: str, status: str):
    """Update conversation status."""
    with get_db() as conn:
        conn.execute("UPDATE conversations SET status = ?, last_active = ? WHERE id = ?",
                     (status, time.time(), conv_id))


def list_conversations(limit: int = 50) -> list[dict]:
    """List recent conversations."""
    with get_db() as conn:
        rows = conn.execute("""
            SELECT c.*, 
                   (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id AND m.role = 'user') as user_turns,
                   (SELECT content FROM messages m WHERE m.conversation_id = c.id ORDER BY m.id DESC LIMIT 1) as last_message
            FROM conversations c
            ORDER BY c.last_active DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def cleanup_old_conversations(max_age_sec: int = 86400 * 30):
    """Remove conversations older than max_age_sec (default 30 days)."""
    cutoff = time.time() - max_age_sec
    with get_db() as conn:
        conn.execute("DELETE FROM conversations WHERE last_active < ?", (cutoff,))


# ════════════════════════════════════════════
# Stats
# ════════════════════════════════════════════

def compute_stats(total_concepts: int) -> dict:
    """Compute learning statistics."""
    streak = refresh_streak()
    progress_list = get_all_progress()

    mastered = sum(1 for p in progress_list if p['status'] == 'mastered')
    learning = sum(1 for p in progress_list if p['status'] == 'learning')
    total_time = sum(p['total_time_sec'] for p in progress_list)

    return {
        'total_concepts': total_concepts,
        'mastered_count': mastered,
        'learning_count': learning,
        'available_count': total_concepts - mastered - learning,
        'locked_count': 0,
        'not_started_count': total_concepts - mastered - learning,
        'total_study_time_sec': total_time,
        'current_streak': streak['current_streak'],
        'longest_streak': streak['longest_streak'],
    }

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
from pathlib import Path
from contextlib import contextmanager
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)

# ── DB file location ──
# In frozen mode (EXE): next to the exe file
# In dev mode: project root / data /
if getattr(sys, 'frozen', False):
    _DB_DIR = Path(sys.executable).parent / "data"
else:
    _DB_DIR = Path(__file__).parent.parent.parent.parent / "data"

_DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = _DB_DIR / "akg_local.db"

_SCHEMA_VERSION = 5


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
                domain_id TEXT NOT NULL DEFAULT 'ai-engineering',
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

        # ── Schema migrations ──
        version = conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] or 1

        if version < 2:
            # V2: Add domain_id to conversations for multi-domain support
            try:
                conn.execute("ALTER TABLE conversations ADD COLUMN domain_id TEXT NOT NULL DEFAULT 'ai-engineering'")
            except Exception:
                pass  # Column already exists (re-run safe)
            conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (2)")
            conn.commit()
            logger.info("SQLite schema migrated to v2 (conversations.domain_id)")

        if version < 3:
            # V3: Add FSRS spaced repetition fields to concept_progress
            _fsrs_columns = [
                ("fsrs_stability", "REAL NOT NULL DEFAULT 0"),
                ("fsrs_difficulty", "REAL NOT NULL DEFAULT 0"),
                ("fsrs_due", "REAL NOT NULL DEFAULT 0"),
                ("fsrs_elapsed_days", "INTEGER NOT NULL DEFAULT 0"),
                ("fsrs_scheduled_days", "INTEGER NOT NULL DEFAULT 0"),
                ("fsrs_reps", "INTEGER NOT NULL DEFAULT 0"),
                ("fsrs_lapses", "INTEGER NOT NULL DEFAULT 0"),
                ("fsrs_state", "INTEGER NOT NULL DEFAULT 0"),
                ("fsrs_last_review", "REAL NOT NULL DEFAULT 0"),
            ]
            for col_name, col_def in _fsrs_columns:
                try:
                    conn.execute(f"ALTER TABLE concept_progress ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass  # Column already exists (re-run safe)
            # Index for efficient due-date queries
            try:
                conn.execute("CREATE INDEX IF NOT EXISTS idx_progress_fsrs_due ON concept_progress(fsrs_due)")
            except Exception:
                pass
            conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (3)")
            conn.commit()
            logger.info("SQLite schema migrated to v3 (FSRS spaced repetition fields)")

        if version < 4:
            # V4: Add BKT (Bayesian Knowledge Tracing) columns to concept_progress
            _bkt_columns = [
                ("bkt_mastery", "REAL NOT NULL DEFAULT 0"),        # Current P(L) — mastery probability
                ("bkt_observations", "INTEGER NOT NULL DEFAULT 0"), # Total observation count
                ("bkt_correct_count", "INTEGER NOT NULL DEFAULT 0"), # Correct observation count
                ("bkt_params_json", "TEXT NOT NULL DEFAULT ''"),    # JSON-encoded BKT params (per-concept)
            ]
            for col_name, col_def in _bkt_columns:
                try:
                    conn.execute(f"ALTER TABLE concept_progress ADD COLUMN {col_name} {col_def}")
                except Exception:
                    pass  # Column already exists (re-run safe)
            conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (4)")
            conn.commit()
            logger.info("SQLite schema migrated to v4 (BKT knowledge tracing fields)")

        if version < 5:
            # V5: Add user_achievements table for achievement system
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS user_achievements (
                    achievement_key TEXT PRIMARY KEY,
                    unlocked_at REAL NOT NULL DEFAULT 0,
                    progress REAL NOT NULL DEFAULT 0,
                    seen INTEGER NOT NULL DEFAULT 0
                );
            """)
            conn.execute("INSERT OR REPLACE INTO schema_version (version) VALUES (5)")
            conn.commit()
            logger.info("SQLite schema migrated to v5 (user_achievements table)")


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
    """Insert or update concept progress — atomic upsert via ON CONFLICT."""
    now = time.time()

    with get_db() as conn:
        conn.execute("""
            INSERT INTO concept_progress (concept_id, status, mastery_score, last_score, sessions, total_time_sec, mastered_at, last_learn_at, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(concept_id) DO UPDATE SET
                status = COALESCE(?, concept_progress.status),
                mastery_score = COALESCE(?, concept_progress.mastery_score),
                last_score = COALESCE(?, concept_progress.last_score),
                sessions = COALESCE(?, concept_progress.sessions),
                total_time_sec = COALESCE(?, concept_progress.total_time_sec),
                mastered_at = COALESCE(?, concept_progress.mastered_at),
                last_learn_at = COALESCE(?, concept_progress.last_learn_at),
                updated_at = ?
        """, (
            concept_id,
            kwargs.get('status', 'not_started'),
            kwargs.get('mastery_score', 0),
            kwargs.get('last_score'),
            kwargs.get('sessions', 0),
            kwargs.get('total_time_sec', 0),
            kwargs.get('mastered_at'),
            kwargs.get('last_learn_at', now),
            now, now,
            # ON CONFLICT SET values
            kwargs.get('status'),
            kwargs.get('mastery_score'),
            kwargs.get('last_score'),
            kwargs.get('sessions'),
            kwargs.get('total_time_sec'),
            kwargs.get('mastered_at'),
            kwargs.get('last_learn_at'),
            now,
        ))

    return get_progress(concept_id) or {}


def start_learning(concept_id: str) -> dict:
    """Mark concept as learning, increment session count.
    C-05 fix: Atomic read-modify-write in a single connection to prevent TOCTOU race.
    """
    now = time.time()
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM concept_progress WHERE concept_id = ?", (concept_id,)
        ).fetchone()
        if row:
            cols = [d[0] for d in conn.execute("SELECT * FROM concept_progress LIMIT 0").description]
            existing = dict(zip(cols, row))
            new_status = 'mastered' if existing['status'] == 'mastered' else 'learning'
            conn.execute(
                """UPDATE concept_progress
                   SET status = ?, sessions = sessions + 1, last_learn_at = ?, updated_at = ?
                   WHERE concept_id = ?""",
                (new_status, now, now, concept_id),
            )
        else:
            conn.execute(
                """INSERT INTO concept_progress
                   (concept_id, status, mastery_score, last_score, sessions, total_time_sec,
                    mastered_at, last_learn_at, created_at, updated_at)
                   VALUES (?, 'learning', 0, NULL, 1, 0, NULL, ?, ?, ?)""",
                (concept_id, now, now, now),
            )
    return get_progress(concept_id) or {}


def record_assessment(concept_id: str, concept_name: str, score: float, mastered: bool) -> dict:
    """Record assessment result, potentially marking as mastered.
    C-06 fix: Never demote a mastered concept back to learning — matches frontend wasMastered guard.
    """
    now = time.time()
    existing = get_progress(concept_id)
    old_score = existing['mastery_score'] if existing else 0
    was_mastered = existing is not None and existing.get('status') == 'mastered'

    # Once mastered, always mastered (demotion protection)
    effective_mastered = mastered or was_mastered
    progress = upsert_progress(
        concept_id,
        status='mastered' if effective_mastered else 'learning',
        mastery_score=max(score, old_score) if effective_mastered else score,
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
                      system_prompt: str, is_milestone: bool = False,
                      domain_id: str = "ai-engineering") -> dict:
    """Create or update a conversation record."""
    now = time.time()
    with get_db() as conn:
        conn.execute("""
            INSERT INTO conversations (id, concept_id, concept_name, domain_id, system_prompt, is_milestone, last_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET last_active = ?, status = 'active'
        """, (conv_id, concept_id, concept_name, domain_id, system_prompt, 1 if is_milestone else 0, now, now, now))
    return {'id': conv_id, 'concept_id': concept_id, 'concept_name': concept_name, 'domain_id': domain_id}


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
# FSRS Spaced Repetition
# ════════════════════════════════════════════

def get_fsrs_card(concept_id: str) -> Optional[dict]:
    """Get FSRS card state for a concept, or None if not found."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT concept_id, fsrs_stability, fsrs_difficulty, fsrs_due,
                      fsrs_elapsed_days, fsrs_scheduled_days, fsrs_reps,
                      fsrs_lapses, fsrs_state, fsrs_last_review
               FROM concept_progress WHERE concept_id = ?""",
            (concept_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        return {
            'concept_id': d['concept_id'],
            'stability': d['fsrs_stability'],
            'difficulty': d['fsrs_difficulty'],
            'due': d['fsrs_due'],
            'elapsed_days': d['fsrs_elapsed_days'],
            'scheduled_days': d['fsrs_scheduled_days'],
            'reps': d['fsrs_reps'],
            'lapses': d['fsrs_lapses'],
            'state': d['fsrs_state'],
            'last_review': d['fsrs_last_review'],
        }


def update_fsrs_card(concept_id: str, card_data: dict) -> None:
    """Update FSRS fields for a concept. Creates concept_progress row if needed."""
    now = time.time()
    with get_db() as conn:
        # Ensure the row exists
        existing = conn.execute(
            "SELECT concept_id FROM concept_progress WHERE concept_id = ?",
            (concept_id,)
        ).fetchone()
        if not existing:
            conn.execute(
                """INSERT INTO concept_progress
                   (concept_id, status, mastery_score, sessions, total_time_sec,
                    created_at, updated_at)
                   VALUES (?, 'not_started', 0, 0, 0, ?, ?)""",
                (concept_id, now, now),
            )
        conn.execute(
            """UPDATE concept_progress SET
                fsrs_stability = ?,
                fsrs_difficulty = ?,
                fsrs_due = ?,
                fsrs_elapsed_days = ?,
                fsrs_scheduled_days = ?,
                fsrs_reps = ?,
                fsrs_lapses = ?,
                fsrs_state = ?,
                fsrs_last_review = ?,
                updated_at = ?
            WHERE concept_id = ?""",
            (
                card_data.get('stability', 0),
                card_data.get('difficulty', 0),
                card_data.get('due', 0),
                card_data.get('elapsed_days', 0),
                card_data.get('scheduled_days', 0),
                card_data.get('reps', 0),
                card_data.get('lapses', 0),
                card_data.get('state', 0),
                card_data.get('last_review', 0),
                now,
                concept_id,
            ),
        )


def get_due_concepts(before: float | None = None, limit: int = 50) -> list[dict]:
    """Get concepts due for review.

    Returns concepts where:
    - fsrs_state > 0 (not New — has been reviewed at least once)
    - fsrs_due <= before (due time has passed)

    Sorted by due date ascending (most overdue first).
    """
    before = before or time.time()
    with get_db() as conn:
        rows = conn.execute(
            """SELECT concept_id, status, mastery_score, fsrs_stability, fsrs_difficulty,
                      fsrs_due, fsrs_elapsed_days, fsrs_scheduled_days, fsrs_reps,
                      fsrs_lapses, fsrs_state, fsrs_last_review
               FROM concept_progress
               WHERE fsrs_state > 0 AND fsrs_due > 0 AND fsrs_due <= ?
               ORDER BY fsrs_due ASC
               LIMIT ?""",
            (before, limit),
        ).fetchall()
        return [dict(r) for r in rows]


# ════════════════════════════════════════════
# BKT Knowledge Tracing
# ════════════════════════════════════════════

def get_bkt_state(concept_id: str) -> Optional[dict]:
    """Get BKT state for a concept, or None if no record exists."""
    with get_db() as conn:
        row = conn.execute(
            """SELECT concept_id, bkt_mastery, bkt_observations, bkt_correct_count, bkt_params_json
               FROM concept_progress WHERE concept_id = ?""",
            (concept_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        # Skip concepts that have never had BKT update (default zeros)
        if d['bkt_observations'] == 0 and d['bkt_mastery'] == 0:
            return None
        return {
            'concept_id': d['concept_id'],
            'p_mastery': d['bkt_mastery'],
            'observations': d['bkt_observations'],
            'correct_count': d['bkt_correct_count'],
            'params_json': d['bkt_params_json'],
        }


def update_bkt_state(concept_id: str, p_mastery: float, observations: int,
                     correct_count: int, params_json: str = '') -> None:
    """Update BKT fields for a concept. Creates concept_progress row if needed."""
    now = time.time()
    with get_db() as conn:
        existing = conn.execute(
            "SELECT concept_id FROM concept_progress WHERE concept_id = ?",
            (concept_id,)
        ).fetchone()
        if not existing:
            conn.execute(
                """INSERT INTO concept_progress
                   (concept_id, status, mastery_score, sessions, total_time_sec,
                    created_at, updated_at, bkt_mastery, bkt_observations, bkt_correct_count, bkt_params_json)
                   VALUES (?, 'not_started', 0, 0, 0, ?, ?, ?, ?, ?, ?)""",
                (concept_id, now, now, p_mastery, observations, correct_count, params_json),
            )
        else:
            conn.execute(
                """UPDATE concept_progress SET
                    bkt_mastery = ?,
                    bkt_observations = ?,
                    bkt_correct_count = ?,
                    bkt_params_json = ?,
                    updated_at = ?
                WHERE concept_id = ?""",
                (p_mastery, observations, correct_count, params_json, now, concept_id),
            )


def get_all_bkt_states() -> list[dict]:
    """Get all concepts that have BKT tracking data (observations > 0)."""
    with get_db() as conn:
        rows = conn.execute(
            """SELECT concept_id, bkt_mastery, bkt_observations, bkt_correct_count, bkt_params_json
               FROM concept_progress
               WHERE bkt_observations > 0
               ORDER BY bkt_mastery DESC""",
        ).fetchall()
        return [dict(r) for r in rows]


# ════════════════════════════════════════════
# Achievements
# ════════════════════════════════════════════

def get_all_achievements() -> list[dict]:
    """Get all unlocked achievements."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT achievement_key, unlocked_at, progress, seen FROM user_achievements"
        ).fetchall()
        return [dict(r) for r in rows]


def get_unlocked_keys() -> set[str]:
    """Get set of all unlocked achievement keys."""
    with get_db() as conn:
        rows = conn.execute("SELECT achievement_key FROM user_achievements").fetchall()
        return {r[0] for r in rows}


def get_unlocked_map() -> dict[str, dict]:
    """Get map of unlocked achievements: {key: {unlocked_at, seen, progress}}."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT achievement_key, unlocked_at, progress, seen FROM user_achievements"
        ).fetchall()
        return {
            r['achievement_key']: {
                'unlocked_at': r['unlocked_at'],
                'progress': r['progress'],
                'seen': bool(r['seen']),
            }
            for r in rows
        }


def unlock_achievement(key: str, progress: float = 100.0) -> bool:
    """Unlock an achievement. Returns True if newly unlocked, False if already existed."""
    import time as _time
    now = _time.time()
    with get_db() as conn:
        existing = conn.execute(
            "SELECT achievement_key FROM user_achievements WHERE achievement_key = ?", (key,)
        ).fetchone()
        if existing:
            return False
        conn.execute(
            "INSERT INTO user_achievements (achievement_key, unlocked_at, progress, seen) VALUES (?, ?, ?, 0)",
            (key, now, progress),
        )
        return True


def mark_achievements_seen(keys: list[str]) -> int:
    """Mark achievements as seen. Returns count of updated rows."""
    if not keys:
        return 0
    with get_db() as conn:
        placeholders = ','.join('?' for _ in keys)
        cursor = conn.execute(
            f"UPDATE user_achievements SET seen = 1 WHERE achievement_key IN ({placeholders}) AND seen = 0",
            keys,
        )
        return cursor.rowcount


def get_unseen_achievements() -> list[dict]:
    """Get achievements that haven't been seen by the user yet."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT achievement_key, unlocked_at, progress FROM user_achievements WHERE seen = 0 ORDER BY unlocked_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


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

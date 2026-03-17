import { Hono } from 'hono';
import type { Env } from '../types';
import seedGraph from '../../data/seed_graph.json';

const app = new Hono<{ Bindings: Env }>();
const seed = seedGraph as any;

/** GET /learning/stats */
app.get('/stats', async (c) => {
  const totalConcepts = parseInt(c.req.query('total_concepts') || '267');
  const db = c.env.DB;
  const mastered = await db.prepare("SELECT COUNT(*) as cnt FROM concept_progress WHERE status = 'mastered'").first<{ cnt: number }>();
  const learning = await db.prepare("SELECT COUNT(*) as cnt FROM concept_progress WHERE status = 'learning'").first<{ cnt: number }>();
  const streak = await db.prepare('SELECT * FROM streak WHERE id = 1').first<any>();

  const masteredCount = mastered?.cnt || 0;
  const learningCount = learning?.cnt || 0;

  return c.json({
    total_concepts: totalConcepts,
    mastered_count: masteredCount,
    learning_count: learningCount,
    available_count: totalConcepts - masteredCount - learningCount,
    locked_count: 0,
    not_started_count: totalConcepts - masteredCount - learningCount,
    total_study_time_sec: 0,
    current_streak: streak?.current_streak || 0,
    longest_streak: streak?.longest_streak || 0,
  });
});

/** GET /learning/progress */
app.get('/progress', async (c) => {
  const db = c.env.DB;
  const { results } = await db.prepare('SELECT * FROM concept_progress').all();
  return c.json(results || []);
});

/** GET /learning/progress/:concept_id */
app.get('/progress/:concept_id', async (c) => {
  const conceptId = c.req.param('concept_id');
  const db = c.env.DB;
  const row = await db.prepare('SELECT * FROM concept_progress WHERE concept_id = ?').bind(conceptId).first();
  if (!row) return c.json({ concept_id: conceptId, status: 'not_started', mastery_score: 0, sessions: 0 });
  return c.json(row);
});

/** POST /learning/start */
app.post('/start', async (c) => {
  const { concept_id } = await c.req.json<{ concept_id: string }>();
  const db = c.env.DB;
  const now = Date.now() / 1000;

  await db.prepare(`
    INSERT INTO concept_progress (concept_id, status, sessions, last_learn_at, created_at, updated_at)
    VALUES (?, 'learning', 1, ?, ?, ?)
    ON CONFLICT(concept_id) DO UPDATE SET
      status = CASE WHEN status = 'mastered' THEN 'mastered' ELSE 'learning' END,
      sessions = sessions + 1,
      last_learn_at = ?,
      updated_at = ?
  `).bind(concept_id, now, now, now, now, now).run();

  // Update streak
  const today = new Date().toISOString().slice(0, 10);
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  const streak = await db.prepare('SELECT * FROM streak WHERE id = 1').first<any>();

  if (streak && streak.last_date !== today) {
    const newCurrent = streak.last_date === yesterday ? streak.current_streak + 1 : 1;
    const newLongest = Math.max(streak.longest_streak, newCurrent);
    await db.prepare('UPDATE streak SET current_streak = ?, longest_streak = ?, last_date = ? WHERE id = 1')
      .bind(newCurrent, newLongest, today).run();
  }

  return c.json({ success: true });
});

/** POST /learning/assess */
app.post('/assess', async (c) => {
  const { concept_id, concept_name, score, mastered } = await c.req.json<{
    concept_id: string; concept_name: string; score: number; mastered: boolean;
  }>();
  const db = c.env.DB;
  const now = Date.now() / 1000;

  await db.prepare(`
    INSERT INTO concept_progress (concept_id, status, mastery_score, last_score, sessions, mastered_at, last_learn_at, created_at, updated_at)
    VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
    ON CONFLICT(concept_id) DO UPDATE SET
      status = ?,
      mastery_score = CASE WHEN ? THEN MAX(mastery_score, ?) ELSE ? END,
      last_score = ?,
      mastered_at = CASE WHEN ? AND mastered_at IS NULL THEN ? ELSE mastered_at END,
      last_learn_at = ?,
      updated_at = ?
  `).bind(
    concept_id, mastered ? 'mastered' : 'learning', score, score, mastered ? now : null, now, now, now,
    mastered ? 'mastered' : 'learning', mastered, score, score, score, mastered, now, now, now,
  ).run();

  // Add history entry
  await db.prepare('INSERT INTO learning_history (concept_id, concept_name, score, mastered, timestamp) VALUES (?, ?, ?, ?, ?)')
    .bind(concept_id, concept_name, score, mastered ? 1 : 0, now).run();

  return c.json({ success: true, mastered });
});

/** GET /learning/history */
app.get('/history', async (c) => {
  const limit = Math.min(parseInt(c.req.query('limit') || '100'), 1000);
  const db = c.env.DB;
  const { results } = await db.prepare('SELECT * FROM learning_history ORDER BY timestamp DESC LIMIT ?').bind(limit).all();
  return c.json(results || []);
});

/** GET /learning/streak */
app.get('/streak', async (c) => {
  const db = c.env.DB;
  const streak = await db.prepare('SELECT * FROM streak WHERE id = 1').first<any>();
  if (!streak) return c.json({ current_streak: 0, longest_streak: 0, last_date: '' });

  // Check if streak needs reset
  const today = new Date().toISOString().slice(0, 10);
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  if (streak.last_date && streak.last_date !== today && streak.last_date !== yesterday) {
    await db.prepare('UPDATE streak SET current_streak = 0 WHERE id = 1').run();
    return c.json({ current_streak: 0, longest_streak: streak.longest_streak, last_date: streak.last_date });
  }
  return c.json(streak);
});

/** POST /learning/sync */
app.post('/sync', async (c) => {
  const { progress, history, streak } = await c.req.json<{
    progress: Record<string, any>; history: any[]; streak?: any;
  }>();
  const db = c.env.DB;
  const now = Date.now() / 1000;
  let syncedProgress = 0;
  let syncedHistory = 0;

  // Input validation (matching FastAPI backend limits)
  const VALID_STATUSES = new Set(['not_started', 'learning', 'mastered', 'available', 'locked', 'reviewing']);
  const progressEntries = Object.entries(progress || {});
  if (progressEntries.length > 500) {
    return c.json({ error: 'progress exceeds 500 entries limit' }, 400);
  }
  const historyEntries = history || [];
  if (historyEntries.length > 1000) {
    return c.json({ error: 'history exceeds 1000 entries limit' }, 400);
  }

  for (const [conceptId, data] of progressEntries) {
    // Status whitelist validation
    const status = VALID_STATUSES.has(data.status) ? data.status : 'not_started';
    // Score clamping to [0, 100]
    const masteryScore = Math.max(0, Math.min(100, Number(data.mastery_score) || 0));
    const lastScore = data.last_score != null ? Math.max(0, Math.min(100, Number(data.last_score))) : null;

    await db.prepare(`
      INSERT INTO concept_progress (concept_id, status, mastery_score, last_score, sessions, total_time_sec, mastered_at, last_learn_at, created_at, updated_at)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT(concept_id) DO UPDATE SET
        status = CASE WHEN excluded.last_learn_at > concept_progress.last_learn_at THEN excluded.status ELSE concept_progress.status END,
        mastery_score = MAX(concept_progress.mastery_score, excluded.mastery_score),
        sessions = MAX(concept_progress.sessions, excluded.sessions),
        last_learn_at = MAX(concept_progress.last_learn_at, excluded.last_learn_at),
        updated_at = ?
    `).bind(
      conceptId, status, masteryScore, lastScore,
      data.sessions || 0, data.total_time_sec || 0, data.mastered_at || null, data.last_learn_at || 0,
      now, now, now,
    ).run();
    syncedProgress++;
  }

  for (const entry of historyEntries) {
    const score = Math.max(0, Math.min(100, Number(entry.score) || 0));
    await db.prepare('INSERT INTO learning_history (concept_id, concept_name, score, mastered, timestamp) VALUES (?, ?, ?, ?, ?)')
      .bind(entry.concept_id, entry.concept_name || entry.concept_id, score, entry.mastered ? 1 : 0, entry.timestamp || now).run();
    syncedHistory++;
  }

  if (streak) {
    await db.prepare('UPDATE streak SET current_streak = MAX(current_streak, ?), longest_streak = MAX(longest_streak, ?), last_date = ? WHERE id = 1')
      .bind(streak.current || 0, streak.longest || 0, streak.lastDate || '').run();
  }

  return c.json({ success: true, synced_progress: syncedProgress, synced_history: syncedHistory });
});

/** GET /learning/recommend */
app.get('/recommend', async (c) => {
  const topK = Math.min(parseInt(c.req.query('top_k') || '5'), 50);
  const db = c.env.DB;

  const { results: allProgress } = await db.prepare('SELECT * FROM concept_progress').all();
  const progressMap: Record<string, any> = {};
  const masteredIds = new Set<string>();
  for (const p of (allProgress || [])) {
    const pp = p as any;
    progressMap[pp.concept_id] = pp;
    if (pp.status === 'mastered') masteredIds.add(pp.concept_id);
  }

  const idToConcept: Record<string, any> = {};
  for (const cc of seed.concepts) idToConcept[cc.id] = cc;

  const prereqMap: Record<string, string[]> = {};
  const depsMap: Record<string, string[]> = {};
  for (const e of seed.edges) {
    if (e.relation_type === 'prerequisite') {
      (prereqMap[e.target_id] ??= []).push(e.source_id);
      (depsMap[e.source_id] ??= []).push(e.target_id);
    }
  }

  const masteredDiffs = [...masteredIds].map(id => idToConcept[id]?.difficulty || 1);
  const currentLevel = masteredDiffs.length > 0 ? masteredDiffs.reduce((a, b) => a + b, 0) / masteredDiffs.length : 1.0;

  const scored: Array<{ concept: any; score: number }> = [];
  for (const cc of seed.concepts) {
    if (masteredIds.has(cc.id)) continue;
    const prereqs = prereqMap[cc.id] || [];
    if (!prereqs.every(p => masteredIds.has(p))) continue;

    let score = 0;
    if (cc.is_milestone) score += 15;
    const optimal = currentLevel + 1;
    score += Math.max(0, 10 - Math.abs(cc.difficulty - optimal) * 2);
    score += Math.min((depsMap[cc.id] || []).length * 2, 10);
    const prog = progressMap[cc.id];
    if (prog?.status === 'learning') { score += 8; if (prog.last_score > 0) score += 5; }
    if (cc.estimated_minutes <= 15) score += 2;
    else if (cc.estimated_minutes <= 25) score += 1;

    scored.push({ concept: cc, score });
  }

  scored.sort((a, b) => b.score - a.score);

  const recommendations = scored.slice(0, topK).map(item => ({
    concept_id: item.concept.id,
    name: item.concept.name,
    subdomain_id: item.concept.subdomain_id,
    difficulty: item.concept.difficulty,
    estimated_minutes: item.concept.estimated_minutes,
    is_milestone: item.concept.is_milestone ?? false,
    score: Math.round(item.score * 10) / 10,
    reason: item.concept.is_milestone ? '🏆 里程碑节点' : '适合当前水平',
    status: progressMap[item.concept.id]?.status || 'not_started',
  }));

  return c.json({
    recommendations,
    current_level: Math.round(currentLevel * 10) / 10,
    mastered_count: masteredIds.size,
    total_concepts: seed.concepts.length,
  });
});

export default app;

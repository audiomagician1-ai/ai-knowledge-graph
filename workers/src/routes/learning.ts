import { Hono } from 'hono';
import type { Env } from '../types';
// Multi-domain seed data imports
import seedAI from '../../data/seed/ai-engineering/seed_graph.json';
import seedMath from '../../data/seed/mathematics/seed_graph.json';
import seedEnglish from '../../data/seed/english/seed_graph.json';
import seedPhysics from '../../data/seed/physics/seed_graph.json';
import seedProduct from '../../data/seed/product-design/seed_graph.json';
import seedFinance from '../../data/seed/finance/seed_graph.json';
import seedPsychology from '../../data/seed/psychology/seed_graph.json';
import seedPhilosophy from '../../data/seed/philosophy/seed_graph.json';
import seedBiology from '../../data/seed/biology/seed_graph.json';
import seedEconomics from '../../data/seed/economics/seed_graph.json';
import seedWriting from '../../data/seed/writing/seed_graph.json';
import seedGameDesign from '../../data/seed/game-design/seed_graph.json';
import seedLevelDesign from '../../data/seed/level-design/seed_graph.json';
import seedGameEngine from '../../data/seed/game-engine/seed_graph.json';
import seedSoftwareEngineering from '../../data/seed/software-engineering/seed_graph.json';
import seedComputerGraphics from '../../data/seed/computer-graphics/seed_graph.json';
import seed3DArt from '../../data/seed/3d-art/seed_graph.json';
import seedConceptDesign from '../../data/seed/concept-design/seed_graph.json';
import seedAnimation from '../../data/seed/animation/seed_graph.json';
import seedTechnicalArt from '../../data/seed/technical-art/seed_graph.json';
import seedVfx from '../../data/seed/vfx/seed_graph.json';
import seedGameAudioMusic from '../../data/seed/game-audio-music/seed_graph.json';
import seedGameUiUx from '../../data/seed/game-ui-ux/seed_graph.json';
import seedNarrativeDesign from '../../data/seed/narrative-design/seed_graph.json';

const app = new Hono<{ Bindings: Env }>();

const DEFAULT_DOMAIN = 'ai-engineering';
const seedMap: Record<string, any> = {
  'ai-engineering': seedAI, 'mathematics': seedMath, 'english': seedEnglish,
  'physics': seedPhysics, 'product-design': seedProduct, 'finance': seedFinance,
  'psychology': seedPsychology, 'philosophy': seedPhilosophy,
  'biology': seedBiology, 'economics': seedEconomics, 'writing': seedWriting,
  'game-design': seedGameDesign,
  'level-design': seedLevelDesign,
  'game-engine': seedGameEngine,
  'software-engineering': seedSoftwareEngineering,
  'computer-graphics': seedComputerGraphics,
  '3d-art': seed3DArt,
  'concept-design': seedConceptDesign,
  'animation': seedAnimation,
  'technical-art': seedTechnicalArt,
  'vfx': seedVfx,
  'game-audio-music': seedGameAudioMusic,
  'game-ui-ux': seedGameUiUx,
  'narrative-design': seedNarrativeDesign,
};
function getSeed(domain: string): any { return seedMap[domain] || seedMap[DEFAULT_DOMAIN]; }

/** GET /learning/stats */
app.get('/stats', async (c) => {
  const totalConcepts = parseInt(c.req.query('total_concepts') || '400');
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
  // Score clamping to [0, 100]
  const clampedScore = Math.max(0, Math.min(100, Number(score) || 0));

  // C-06 fix: Never demote mastered → learning (matches FastAPI sqlite_client.py)
  const existing = await db.prepare('SELECT status, mastery_score, mastered_at FROM concept_progress WHERE concept_id = ?').bind(concept_id).first<any>();
  const wasMastered = existing?.status === 'mastered';
  const effectiveMastered = mastered || wasMastered;
  const effectiveStatus = effectiveMastered ? 'mastered' : 'learning';
  const effectiveScore = effectiveMastered ? Math.max(clampedScore, existing?.mastery_score || 0) : clampedScore;
  const effectiveMasteredAt = effectiveMastered && !existing?.mastered_at ? now : (existing?.mastered_at || null);

  await db.prepare(`
    INSERT INTO concept_progress (concept_id, status, mastery_score, last_score, sessions, mastered_at, last_learn_at, created_at, updated_at)
    VALUES (?, ?, ?, ?, 1, ?, ?, ?, ?)
    ON CONFLICT(concept_id) DO UPDATE SET
      status = ?,
      mastery_score = ?,
      last_score = ?,
      mastered_at = ?,
      last_learn_at = ?,
      updated_at = ?
  `).bind(
    concept_id, effectiveStatus, effectiveScore, clampedScore, effectiveMasteredAt, now, now, now,
    effectiveStatus, effectiveScore, clampedScore, effectiveMasteredAt, now, now,
  ).run();

  // Add history entry
  await db.prepare('INSERT INTO learning_history (concept_id, concept_name, score, mastered, timestamp) VALUES (?, ?, ?, ?, ?)')
    .bind(concept_id, concept_name, clampedScore, effectiveMastered ? 1 : 0, now).run();

  return c.json({ success: true, mastered: effectiveMastered });
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
        status = CASE
          WHEN concept_progress.status = 'mastered' THEN 'mastered'
          WHEN excluded.last_learn_at > concept_progress.last_learn_at THEN excluded.status
          ELSE concept_progress.status
        END,
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
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const seed = getSeed(domain);
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
  const currentLevel = masteredDiffs.length > 0 ? masteredDiffs.reduce((a, b) => a + b, 0) / masteredDiffs.length : 0.0;
  const isNewUser = masteredIds.size === 0;

  const scored: Array<{ concept: any; score: number }> = [];
  for (const cc of seed.concepts) {
    if (masteredIds.has(cc.id)) continue;
    const prereqs = prereqMap[cc.id] || [];
    if (!prereqs.every(p => masteredIds.has(p))) continue;

    let score = 0;
    const diff = cc.difficulty;

    if (isNewUser) {
      // New user: strongly prefer lowest difficulty (dominant factor)
      // diff=1 → 50, diff=2 → 40, diff=3 → 30, diff=4 → 20, diff=5 → 10
      score += Math.max(0, 60 - diff * 10);
      if (cc.is_milestone) score += 3;
      score += Math.min((depsMap[cc.id] || []).length * 0.5, 3);
      if (cc.estimated_minutes <= 15) score += 1;
    } else {
      if (cc.is_milestone) score += 15;
      const optimal = currentLevel + 1;
      score += Math.max(0, 10 - Math.abs(diff - optimal) * 2);
      score += Math.min((depsMap[cc.id] || []).length * 2, 10);
      const prog = progressMap[cc.id];
      if (prog?.status === 'learning') { score += 8; if (prog.last_score > 0) score += 5; }
      if (cc.estimated_minutes <= 15) score += 2;
      else if (cc.estimated_minutes <= 25) score += 1;
    }

    scored.push({ concept: cc, score });
  }

  // Sort by score descending, then difficulty ascending, then id (deterministic tiebreaker)
  scored.sort((a, b) => b.score - a.score || a.concept.difficulty - b.concept.difficulty || a.concept.id.localeCompare(b.concept.id));

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

/**
 * supabase-sync.ts — Supabase cloud sync for logged-in users.
 * 
 * Handles:
 * - Upload local learning data to Supabase (first-login migration)
 * - Download cloud data to merge with local (cross-device restore)
 * - Per-action dual-write (learning progress + history)
 * - Conversation sync
 * 
 * Merge strategy: last_learn_at wins (consistent with existing importData).
 * All operations are fire-and-forget safe — errors logged, never thrown to UI.
 */

import { supabase } from '../api/supabase';
import { onAuthLogin, useAuthStore } from './auth';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('Sync');
import type { ConceptProgress, LearningHistory } from './learning';
import { useLearningStore } from './learning';
import { useDomainStore } from './domain';

// ════════════════════════════════════════════
// Helpers
// ════════════════════════════════════════════

function getUserId(): string | null {
  return useAuthStore.getState().user?.id ?? null;
}

export function isLoggedIn(): boolean {
  return useAuthStore.getState().isAuthenticated();
}

/**
 * Map local ConceptStatus to Supabase DB-compatible status.
 * DB CHECK constraint: ('locked', 'available', 'learning', 'reviewing', 'mastered')
 * Local statuses: 'not_started' | 'learning' | 'reviewing' | 'mastered'
 * 'not_started' has no DB equivalent → map to 'available' (visible but not learned)
 */
function toDbStatus(localStatus: string): string {
  if (localStatus === 'not_started') return 'available';
  return localStatus;
}

// ════════════════════════════════════════════
// Progress: Upload / Download / Upsert
// ════════════════════════════════════════════

/** Get current active domain for DB operations */
function getActiveDomainId(): string {
  return useDomainStore.getState().activeDomain;
}

/** Build the DB row from a ConceptProgress (reused by sync and write) */
function buildProgressRow(uid: string, p: ConceptProgress) {
  return {
    user_id: uid,
    concept_id: p.concept_id,
    domain_id: getActiveDomainId(),
    status: toDbStatus(p.status),
    mastery_level: (p.mastery_score || 0) / 100,
    total_sessions: p.sessions || 0,
    total_time_sec: p.total_time_sec || 0,
    feynman_score: p.last_score ? p.last_score / 100 : null,
    last_feynman_at: p.mastered_at ? new Date(p.mastered_at).toISOString() : null,
    updated_at: new Date(p.last_learn_at || Date.now()).toISOString(),
  };
}

/** Upload a single concept progress to Supabase (fire-and-forget) */
export async function syncProgressToCloud(p: ConceptProgress): Promise<void> {
  const uid = getUserId();
  if (!uid) return;
  try {
    const { error } = await supabase.from('user_concept_status')
      .upsert(buildProgressRow(uid, p), { onConflict: 'user_id,concept_id,domain_id' });
    if (error) log.warn('Upsert progress failed', { conceptId: p.concept_id, err: error.message });
  } catch (err) {
    log.warn('Failed to sync progress', { conceptId: p.concept_id, err: (err as Error).message });
  }
}

/**
 * Write a single concept progress to Supabase — returns true on success.
 * Used by Supabase-first path (logged-in users) where we need to know if the write succeeded.
 * On failure, callers should enqueue to offline queue.
 */
export async function writeProgressToCloud(p: ConceptProgress): Promise<boolean> {
  const uid = getUserId();
  if (!uid) return false;
  try {
    const { error } = await supabase.from('user_concept_status')
      .upsert(buildProgressRow(uid, p), { onConflict: 'user_id,concept_id,domain_id' });
    if (error) {
      log.warn('writeProgress failed', { conceptId: p.concept_id, err: error.message });
      return false;
    }
    return true;
  } catch (err) {
    log.warn('writeProgress error', { conceptId: p.concept_id, err: (err as Error).message });
    return false;
  }
}

/** Download all progress from Supabase for current user */
export async function downloadProgressFromCloud(): Promise<Record<string, ConceptProgress>> {
  const uid = getUserId();
  if (!uid) return {};
  try {
    const { data, error } = await supabase
      .from('user_concept_status')
      .select('*')
      .eq('user_id', uid)
      .eq('domain_id', getActiveDomainId());
    if (error || !data) return {};
    const result: Record<string, ConceptProgress> = {};
    const validStatuses = new Set(['not_started', 'learning', 'mastered']);
    for (const row of data) {
      // C-05: Whitelist status values to prevent invalid data propagation
      // Map DB statuses back to local statuses: 'available'→'not_started', 'reviewing'→'learning'
      let rawStatus = row.status;
      if (rawStatus === 'available' || rawStatus === 'locked') rawStatus = 'not_started';
      else if (rawStatus === 'reviewing') rawStatus = 'learning';
      const safeStatus = validStatuses.has(rawStatus) ? rawStatus : 'learning';
      result[row.concept_id] = {
        concept_id: row.concept_id,
        status: safeStatus as any,
        mastery_score: (row.mastery_level || 0) * 100,
        last_score: row.feynman_score ? row.feynman_score * 100 : undefined,
        sessions: row.total_sessions || 0,
        total_time_sec: row.total_time_sec || 0,
        mastered_at: row.last_feynman_at ? new Date(row.last_feynman_at).getTime() : undefined,
        last_learn_at: new Date(row.updated_at || row.created_at).getTime(),
      };
    }
    return result;
  } catch (err) {
    log.warn('Failed to download progress', { err: (err as Error).message });
    return {};
  }
}

// ════════════════════════════════════════════
// History: Upload / Download
// ════════════════════════════════════════════

/** Upload a single learning event to Supabase (fire-and-forget) */
export async function syncHistoryToCloud(
  conceptId: string, conceptName: string, score: number, mastered: boolean
): Promise<void> {
  const uid = getUserId();
  if (!uid) return;
  try {
    const { error } = await supabase.from('learning_events').insert({
      user_id: uid,
      concept_id: conceptId,
      event_type: mastered ? 'mastered' : 'feynman_attempt',
      payload: { concept_name: conceptName, score, mastered },
    });
    if (error) log.warn('Insert history failed', { conceptId, err: error.message });
  } catch (err) {
    log.warn('Failed to sync history event', { err: (err as Error).message });
  }
}

/**
 * Write a single learning event to Supabase — returns true on success.
 * Used by Supabase-first path (logged-in users).
 */
export async function writeHistoryToCloud(
  conceptId: string, conceptName: string, score: number, mastered: boolean
): Promise<boolean> {
  const uid = getUserId();
  if (!uid) return false;
  try {
    const { error } = await supabase.from('learning_events').insert({
      user_id: uid,
      concept_id: conceptId,
      event_type: mastered ? 'mastered' : 'feynman_attempt',
      payload: { concept_name: conceptName, score, mastered },
    });
    if (error) {
      log.warn('writeHistory failed', { conceptId, err: error.message });
      return false;
    }
    return true;
  } catch (err) {
    log.warn('writeHistory error', { err: (err as Error).message });
    return false;
  }
}

/** Download learning history from Supabase */
export async function downloadHistoryFromCloud(limit = 200): Promise<LearningHistory[]> {
  const uid = getUserId();
  if (!uid) return [];
  try {
    const { data, error } = await supabase
      .from('learning_events')
      .select('*')
      .eq('user_id', uid)
      .in('event_type', ['feynman_attempt', 'mastered'])
      .order('created_at', { ascending: false })
      .limit(limit);
    if (error || !data) return [];
    return data.map((row: any) => ({
      concept_id: row.concept_id,
      concept_name: row.payload?.concept_name || row.concept_id,
      score: row.payload?.score ?? 0,
      mastered: row.payload?.mastered ?? false,
      timestamp: new Date(row.created_at).getTime(),
    }));
  } catch (err) {
    log.warn('Failed to download history', { err: (err as Error).message });
    return [];
  }
}

// ════════════════════════════════════════════
// Conversations: Sync
// ════════════════════════════════════════════

export interface CloudConversation {
  id: string;
  concept_id: string;
  messages: any[];
  summary?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

/** Sync a single conversation to Supabase */
export async function syncConversationToCloud(
  convId: string, conceptId: string, messages: any[], status = 'active'
): Promise<void> {
  const uid = getUserId();
  if (!uid) return;
  try {
    await supabase.from('conversations').upsert({
      id: convId,
      user_id: uid,
      concept_id: conceptId,
      messages: messages,
      status,
      updated_at: new Date().toISOString(),
    }, { onConflict: 'id' });
  } catch (err) {
    log.warn('Failed to sync conversation', { convId, err: (err as Error).message });
  }
}

/** Download conversations from Supabase */
export async function downloadConversationsFromCloud(limit = 50): Promise<CloudConversation[]> {
  const uid = getUserId();
  if (!uid) return [];
  try {
    const { data, error } = await supabase
      .from('conversations')
      .select('*')
      .eq('user_id', uid)
      .order('updated_at', { ascending: false })
      .limit(limit);
    if (error || !data) return [];
    return data as CloudConversation[];
  } catch (err) {
    log.warn('Failed to download conversations', { err: (err as Error).message });
    return [];
  }
}

// ════════════════════════════════════════════
// Full Sync (login-triggered)
// ════════════════════════════════════════════

/** Guard against concurrent fullSync calls (e.g. rapid login/logout) */
let _syncing = false;

/**
 * Full bidirectional sync triggered on login.
 * Order: Download first → Merge → Upload merged (prevents overwriting newer cloud data).
 * 1. Download cloud data
 * 2. Merge: last_learn_at wins (local vs cloud)
 * 3. Upload only merged result to cloud
 * 4. Write merged result back to localStorage
 */
export async function fullSync(): Promise<{
  uploadedProgress: number;
  downloadedProgress: number;
  mergedProgress: number;
}> {
  if (_syncing) return { uploadedProgress: 0, downloadedProgress: 0, mergedProgress: 0 };
  _syncing = true;
  try {
    const store = useLearningStore.getState();
    const localProgress = store.progress;
    const localHistory = store.history;

    // 1. Download cloud data FIRST (prevents overwriting newer cloud data)
    const cloudProgress = await downloadProgressFromCloud();
    const cloudHistory = await downloadHistoryFromCloud();

    // 2. Merge progress: last_learn_at wins
    const merged: Record<string, ConceptProgress> = {};
    const allIds = new Set([...Object.keys(localProgress), ...Object.keys(cloudProgress)]);
    let mergedCount = 0;
    for (const cid of allIds) {
      const local = localProgress[cid];
      const cloud = cloudProgress[cid];
      if (local && cloud) {
        // M-10: Safe comparison — fallback to 0 when timestamps are undefined/NaN
        const cloudTs = cloud.last_learn_at || 0;
        const localTs = local.last_learn_at || 0;
        merged[cid] = cloudTs >= localTs ? cloud : local;
        mergedCount++;
      } else {
        merged[cid] = (local || cloud)!;
      }
    }

    // Merge history (deduplicate by concept_id + timestamp)
    const historySet = new Set<string>();
    const allHistory: LearningHistory[] = [];
    for (const h of [...localHistory, ...cloudHistory]) {
      const key = `${h.concept_id}-${h.timestamp}`;
      if (!historySet.has(key)) {
        allHistory.push(h);
        historySet.add(key);
      }
    }
    allHistory.sort((a, b) => a.timestamp - b.timestamp);
    const mergedHistory = allHistory.slice(-500);

    // 3. Upload merged progress to cloud (M-04 fix: batch upsert instead of N individual requests)
    const progressEntries = Object.values(merged);
    const uid = getUserId();
    let uploadedProgress = 0;
    if (uid && progressEntries.length > 0) {
      const BATCH_SIZE = 50;
      for (let i = 0; i < progressEntries.length; i += BATCH_SIZE) {
        const batch = progressEntries.slice(i, i + BATCH_SIZE);
        const rows = batch.map(p => buildProgressRow(uid, p));
        try {
          const { error } = await supabase.from('user_concept_status')
            .upsert(rows, { onConflict: 'user_id,concept_id,domain_id' });
          if (error) log.warn('Batch upsert failed', { err: error.message });
        } catch (err) {
          log.warn('Batch upsert error', { err: (err as Error).message });
        }
        uploadedProgress += batch.length;
      }
    }

    // Upload only history entries newer than last sync (avoid duplicates)
    const lastSyncTs = Number(localStorage.getItem('akg-last-cloud-sync-ts') || '0');
    const newHistory = localHistory.filter(h => h.timestamp > lastSyncTs);
    for (const h of newHistory.slice(-100)) {
      await syncHistoryToCloud(h.concept_id, h.concept_name, h.score, h.mastered);
    }
    localStorage.setItem('akg-last-cloud-sync-ts', String(Date.now()));

    // 4. Write merged result to local store
    store.replaceData({
      progress: merged,
      history: mergedHistory,
      streak: store.streak, // streak stays local
    });

    log.info('Full sync done', { uploaded: uploadedProgress, cloud: Object.keys(cloudProgress).length, merged: mergedCount });

    return {
      uploadedProgress,
      downloadedProgress: Object.keys(cloudProgress).length,
      mergedProgress: mergedCount,
    };
  } finally {
    _syncing = false;
  }
}

// ════════════════════════════════════════════
// Auto-register login callback
// ════════════════════════════════════════════

onAuthLogin(async (_userId: string) => {
  log.info('Login detected, starting full sync...');
  try {
    await fullSync();
  } catch (err) {
    log.warn('Full sync failed', { err: (err as Error).message });
  }
});

// ════════════════════════════════════════════
// Offline queue flush — auto-replay on connectivity restore
// ════════════════════════════════════════════

import { registerOnlineFlush, flushQueue } from './offline-queue';
/** Replay a queued progress write */
async function _replayProgress(data: Record<string, unknown>): Promise<boolean> {
  return writeProgressToCloud(data as unknown as ConceptProgress);
}

/** Replay a queued history write */
async function _replayHistory(conceptId: string, conceptName: string, score: number, mastered: boolean): Promise<boolean> {
  return writeHistoryToCloud(conceptId, conceptName, score, mastered);
}

const _queueWriters = { writeProgress: _replayProgress, writeHistory: _replayHistory };

// Register online/visibility flush listeners
registerOnlineFlush(_queueWriters);

// Also flush when login succeeds (in case items queued while offline then user logs in)
onAuthLogin(async () => {
  try {
    await flushQueue(_queueWriters);
  } catch { /* ignore */ }
});

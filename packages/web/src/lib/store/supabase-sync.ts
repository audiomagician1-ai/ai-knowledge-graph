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
import type { ConceptProgress, LearningHistory } from './learning';
import { useLearningStore } from './learning';

// ════════════════════════════════════════════
// Helpers
// ════════════════════════════════════════════

function getUserId(): string | null {
  return useAuthStore.getState().user?.id ?? null;
}

function isLoggedIn(): boolean {
  return useAuthStore.getState().isAuthenticated();
}

// ════════════════════════════════════════════
// Progress: Upload / Download / Upsert
// ════════════════════════════════════════════

/** Upload a single concept progress to Supabase */
export async function syncProgressToCloud(p: ConceptProgress): Promise<void> {
  const uid = getUserId();
  if (!uid) return;
  try {
    await supabase.from('user_concept_status').upsert({
      user_id: uid,
      concept_id: p.concept_id,
      status: p.status,
      mastery_level: (p.mastery_score || 0) / 100,
      total_sessions: p.sessions || 0,
      total_time_sec: p.total_time_sec || 0,
      feynman_score: p.last_score ? p.last_score / 100 : null,
      last_feynman_at: p.mastered_at ? new Date(p.mastered_at).toISOString() : null,
      updated_at: new Date(p.last_learn_at || Date.now()).toISOString(),
    }, { onConflict: 'user_id,concept_id' });
  } catch (err) {
    console.warn('[sync] Failed to sync progress:', p.concept_id, err);
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
      .eq('user_id', uid);
    if (error || !data) return {};
    const result: Record<string, ConceptProgress> = {};
    for (const row of data) {
      result[row.concept_id] = {
        concept_id: row.concept_id,
        status: row.status === 'reviewing' ? 'learning' : row.status as any,
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
    console.warn('[sync] Failed to download progress:', err);
    return {};
  }
}

// ════════════════════════════════════════════
// History: Upload / Download
// ════════════════════════════════════════════

/** Upload a single learning event to Supabase */
export async function syncHistoryToCloud(
  conceptId: string, conceptName: string, score: number, mastered: boolean
): Promise<void> {
  const uid = getUserId();
  if (!uid) return;
  try {
    await supabase.from('learning_events').insert({
      user_id: uid,
      concept_id: conceptId,
      event_type: mastered ? 'mastered' : 'feynman_attempt',
      payload: { concept_name: conceptName, score, mastered },
    });
  } catch (err) {
    console.warn('[sync] Failed to sync history event:', err);
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
      score: row.payload?.score || 0,
      mastered: row.payload?.mastered || false,
      timestamp: new Date(row.created_at).getTime(),
    }));
  } catch (err) {
    console.warn('[sync] Failed to download history:', err);
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
    console.warn('[sync] Failed to sync conversation:', convId, err);
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
    console.warn('[sync] Failed to download conversations:', err);
    return [];
  }
}

// ════════════════════════════════════════════
// Full Sync (login-triggered)
// ════════════════════════════════════════════

/**
 * Full bidirectional sync triggered on login.
 * 1. Upload local data to cloud (first-login migration)
 * 2. Download cloud data
 * 3. Merge: last_learn_at wins
 * 4. Write merged result back to localStorage
 */
export async function fullSync(): Promise<{
  uploadedProgress: number;
  downloadedProgress: number;
  mergedProgress: number;
}> {
  // Use static import (no circular: learning→supabase-sync exports, supabase-sync→learning store)
  const store = useLearningStore.getState();

  const localProgress = store.progress;
  const localHistory = store.history;

  // 1. Upload all local progress to cloud
  let uploadedProgress = 0;
  const entries = Object.values(localProgress);
  for (const p of entries) {
    await syncProgressToCloud(p);
    uploadedProgress++;
  }

  // Upload local history events
  for (const h of localHistory.slice(-100)) {
    await syncHistoryToCloud(h.concept_id, h.concept_name, h.score, h.mastered);
  }

  // 2. Download cloud data
  const cloudProgress = await downloadProgressFromCloud();
  const cloudHistory = await downloadHistoryFromCloud();

  // 3. Merge: last_learn_at wins
  const merged: Record<string, ConceptProgress> = { ...localProgress };
  let mergedCount = 0;
  for (const [cid, cp] of Object.entries(cloudProgress)) {
    const local = merged[cid];
    if (!local || cp.last_learn_at > local.last_learn_at) {
      merged[cid] = cp;
      mergedCount++;
    }
  }

  // Merge history (deduplicate by concept_id + timestamp)
  const historySet = new Set(localHistory.map(h => `${h.concept_id}-${h.timestamp}`));
  const mergedHistory = [...localHistory];
  for (const ch of cloudHistory) {
    const key = `${ch.concept_id}-${ch.timestamp}`;
    if (!historySet.has(key)) {
      mergedHistory.push(ch);
      historySet.add(key);
    }
  }
  mergedHistory.sort((a, b) => a.timestamp - b.timestamp);

  // 4. Write merged result to local store
  store.replaceData({
    progress: merged,
    history: mergedHistory.slice(-500),
    streak: store.streak, // streak stays local
  });

  console.log(`[sync] Full sync done: uploaded=${uploadedProgress}, cloud=${Object.keys(cloudProgress).length}, merged=${mergedCount}`);

  return {
    uploadedProgress,
    downloadedProgress: Object.keys(cloudProgress).length,
    mergedProgress: mergedCount,
  };
}

// ════════════════════════════════════════════
// Auto-register login callback
// ════════════════════════════════════════════

onAuthLogin(async (_userId: string) => {
  console.log('[sync] Login detected, starting full sync...');
  try {
    await fullSync();
  } catch (err) {
    console.warn('[sync] Full sync failed:', err);
  }
});

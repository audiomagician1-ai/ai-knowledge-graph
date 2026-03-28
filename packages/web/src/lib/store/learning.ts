import { create } from 'zustand';
import type { LearningStats, ConceptStatus } from '@akg/shared';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('Learning');
import {
  apiStartLearning, apiRecordAssessment,
  apiFetchStats, apiSyncToBackend,
} from '@/lib/api/learning-api';
import {
  syncProgressToCloud, syncHistoryToCloud,
  writeProgressToCloud, writeHistoryToCloud,
  isLoggedIn,
} from './supabase-sync';
import { enqueue } from './offline-queue';

// ========================================
// Simplified concept progress for anonymous users
// ========================================
export interface ConceptProgress {
  concept_id: string;
  status: ConceptStatus;
  mastery_score: number; // 0-100, from assessment
  last_score?: number;
  sessions: number;
  total_time_sec: number;
  mastered_at?: number; // timestamp
  last_learn_at: number; // timestamp
}

// ========================================
// Edge map for prerequisite-based unlocking
// ========================================
export interface PrereqEdge {
  source: string; // prerequisite concept
  target: string; // dependent concept
}

/** Build a map: conceptId → list of prerequisite concept IDs */
function buildPrereqMap(edges: PrereqEdge[]): Map<string, string[]> {
  const map = new Map<string, string[]>();
  for (const e of edges) {
    const existing = map.get(e.target) || [];
    existing.push(e.source);
    map.set(e.target, existing);
  }
  return map;
}

/** Build reverse map: conceptId → list of dependent concept IDs */
function buildDependentsMap(edges: PrereqEdge[]): Map<string, string[]> {
  const map = new Map<string, string[]>();
  for (const e of edges) {
    const existing = map.get(e.source) || [];
    existing.push(e.target);
    map.set(e.source, existing);
  }
  return map;
}

/** Check if a concept's prerequisites are all mastered */
function arePrereqsMet(
  conceptId: string,
  prereqMap: Map<string, string[]>,
  progress: Record<string, ConceptProgress>,
): boolean {
  const prereqs = prereqMap.get(conceptId);
  if (!prereqs || prereqs.length === 0) return true; // no prereqs = always available
  return prereqs.every((pid) => progress[pid]?.status === 'mastered');
}

/** Get all concepts that become "recommended" after a node is mastered */
function getNewlyUnlocked(
  masteredId: string,
  dependentsMap: Map<string, string[]>,
  prereqMap: Map<string, string[]>,
  progress: Record<string, ConceptProgress>,
): string[] {
  const dependents = dependentsMap.get(masteredId) || [];
  return dependents.filter((depId) => {
    // Only concepts not yet mastered that now have all prereqs met
    const depStatus = progress[depId]?.status;
    if (depStatus === 'mastered') return false;
    return arePrereqsMet(depId, prereqMap, progress);
  });
}

export interface LearningHistory {
  concept_id: string;
  concept_name: string;
  score: number;
  mastered: boolean;
  timestamp: number;
}

// ========================================
// localStorage persistence — per-domain keys
// ========================================
const LEGACY_STORAGE_KEY = 'akg-learning';        // v1 flat key (pre-7.5)
const LEGACY_HISTORY_KEY = 'akg-learning-history'; // v1 flat key (pre-7.5)
const STREAK_KEY = 'akg-streak'; // Global — not domain-scoped

/** Get domain-scoped storage key */
export function storageKeyForDomain(domain: string): string {
  return `akg-learning:${domain}`;
}

/** Get domain-scoped history key */
export function historyKeyForDomain(domain: string): string {
  return `akg-learning-history:${domain}`;
}

/**
 * One-time migration: move legacy flat keys to domain-scoped keys.
 * Only runs when legacy data exists AND the target domain key is empty.
 * Returns true if migration occurred.
 */
export function migrateLegacyStorage(targetDomain: string = 'ai-engineering'): boolean {
  try {
    const legacyProgress = localStorage.getItem(LEGACY_STORAGE_KEY);
    const domainKey = storageKeyForDomain(targetDomain);
    // Only migrate if legacy data exists and domain key doesn't
    if (legacyProgress && !localStorage.getItem(domainKey)) {
      localStorage.setItem(domainKey, legacyProgress);
      // Migrate history too
      const legacyHistory = localStorage.getItem(LEGACY_HISTORY_KEY);
      if (legacyHistory) {
        localStorage.setItem(historyKeyForDomain(targetDomain), legacyHistory);
      }
      // Remove legacy keys after successful migration
      localStorage.removeItem(LEGACY_STORAGE_KEY);
      localStorage.removeItem(LEGACY_HISTORY_KEY);
      log.info('Migrated legacy storage to domain', { targetDomain });
      return true;
    }
  } catch (e) {
    log.warn('Legacy storage migration failed', { err: (e as Error).message });
  }
  return false;
}

/**
 * Peek at another domain's learning progress without switching the active domain.
 * Reads directly from localStorage — safe to call from any component.
 * Returns { mastered, learning, total } counts (total = mastered + learning + not_started).
 */
export function peekDomainProgress(domain: string): { mastered: number; learning: number; total: number } {
  const key = storageKeyForDomain(domain);
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return { mastered: 0, learning: 0, total: 0 };
    const parsed = JSON.parse(raw);
    const progress: Record<string, { status?: string }> = parsed?.progress || {};
    let mastered = 0;
    let learning = 0;
    for (const val of Object.values(progress)) {
      if (val?.status === 'mastered') mastered++;
      else if (val?.status === 'learning') learning++;
    }
    return { mastered, learning, total: mastered + learning };
  } catch {
    return { mastered: 0, learning: 0, total: 0 };
  }
}

/** Current active domain for storage — set by switchStorageDomain() */
let _activeDomain = 'ai-engineering';

/** Check if localStorage is available and writable */
function verifyStorageAvailable(): boolean {
  const testKey = '__akg_storage_test__';
  try {
    localStorage.setItem(testKey, '1');
    const val = localStorage.getItem(testKey);
    localStorage.removeItem(testKey);
    return val === '1';
  } catch {
    return false;
  }
}

/** Storage diagnostic info — callable from browser console: window.__akgDiag() */
export function getStorageDiagnostics(): {
  storageAvailable: boolean;
  progressEntries: number;
  historyEntries: number;
  streakData: StreakData | null;
  rawSizes: { progress: number; history: number; streak: number };
} {
  const storageAvailable = verifyStorageAvailable();
  const progressKey = storageKeyForDomain(_activeDomain);
  const historyKey = historyKeyForDomain(_activeDomain);
  const progressRaw = localStorage.getItem(progressKey) || '';
  const historyRaw = localStorage.getItem(historyKey) || '';
  const streakRaw = localStorage.getItem(STREAK_KEY) || '';
  let progressEntries = 0;
  let historyEntries = 0;
  let streakData: StreakData | null = null;
  try {
    const p = JSON.parse(progressRaw);
    progressEntries = Object.keys(p?.progress || {}).length;
  } catch { /* empty */ }
  try {
    const h = JSON.parse(historyRaw);
    historyEntries = Array.isArray(h) ? h.length : 0;
  } catch { /* empty */ }
  try { streakData = JSON.parse(streakRaw); } catch { /* empty */ }
  return {
    storageAvailable,
    progressEntries,
    historyEntries,
    streakData,
    rawSizes: { progress: progressRaw.length, history: historyRaw.length, streak: streakRaw.length },
  };
}

// Expose diagnostics on window for debugging
if (typeof window !== 'undefined') {
  (window as any).__akgDiag = getStorageDiagnostics;
}

// Verify at load time
const _storageOk = verifyStorageAvailable();
if (!_storageOk) {
  log.error('localStorage is NOT available! Learning data will NOT be persisted. Check browser privacy settings or storage quota.');
}

interface PersistedData {
  progress: Record<string, ConceptProgress>;
}

/** Validate a single ConceptProgress entry */
function isValidProgress(p: unknown): p is ConceptProgress {
  if (!p || typeof p !== 'object') return false;
  const obj = p as Record<string, unknown>;
  return typeof obj.concept_id === 'string' &&
    typeof obj.status === 'string' &&
    typeof obj.mastery_score === 'number' &&
    typeof obj.last_learn_at === 'number';
}

function loadProgress(domain?: string): Record<string, ConceptProgress> {
  const key = storageKeyForDomain(domain || _activeDomain);
  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      const parsed: PersistedData = JSON.parse(raw);
      const progress = parsed.progress || {};
      // Validate entries, skip corrupted ones
      const validated: Record<string, ConceptProgress> = {};
      for (const [k, val] of Object.entries(progress)) {
        if (isValidProgress(val)) {
          validated[k] = val;
        } else {
          log.warn('Skipped corrupted progress entry', { key: k });
        }
      }
      return validated;
    }
  } catch (e) {
    log.warn('Failed to load progress from localStorage', { err: (e as Error).message });
  }
  return {};
}

function saveProgress(progress: Record<string, ConceptProgress>, domain?: string): boolean {
  const key = storageKeyForDomain(domain || _activeDomain);
  try {
    const data: PersistedData = { progress };
    const json = JSON.stringify(data);
    localStorage.setItem(key, json);
    // Verify write succeeded
    const readBack = localStorage.getItem(key);
    if (!readBack) {
      log.error('localStorage write verification failed: readback is null');
      return false;
    }
    return true;
  } catch (e) {
    log.error('Failed to save progress to localStorage', { err: (e as Error).message });
    return false;
  }
}

function loadHistory(domain?: string): LearningHistory[] {
  const key = historyKeyForDomain(domain || _activeDomain);
  try {
    const raw = localStorage.getItem(key);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed)) return [];
      // Validate entries
      return parsed.filter((h: unknown) => {
        if (!h || typeof h !== 'object') return false;
        const obj = h as Record<string, unknown>;
        return typeof obj.concept_id === 'string' &&
          typeof obj.score === 'number' &&
          typeof obj.timestamp === 'number';
      });
    }
  } catch (e) {
    log.warn('Failed to load history from localStorage', { err: (e as Error).message });
  }
  return [];
}

function saveHistory(history: LearningHistory[], domain?: string): boolean {
  const key = historyKeyForDomain(domain || _activeDomain);
  try {
    // Keep last 100 entries
    const trimmed = history.slice(-100);
    localStorage.setItem(key, JSON.stringify(trimmed));
    return true;
  } catch (e) {
    log.error('Failed to save history to localStorage', { err: (e as Error).message });
    return false;
  }
}

interface StreakData {
  current: number;
  longest: number;
  lastDate: string; // YYYY-MM-DD
}

function loadStreak(): StreakData {
  try {
    const raw = localStorage.getItem(STREAK_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return { current: 0, longest: 0, lastDate: '' };
}

function saveStreak(streak: StreakData): boolean {
  try {
    localStorage.setItem(STREAK_KEY, JSON.stringify(streak));
    return true;
  } catch (e) {
    log.error('Failed to save streak to localStorage', { err: (e as Error).message });
    return false;
  }
}

/** Format a Date object to YYYY-MM-DD in local timezone */
function formatDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** Get today's date string in local timezone (YYYY-MM-DD) */
function todayStr(): string {
  return formatDate(new Date());
}

/** Get yesterday's date string in local timezone */
function yesterdayStr(): string {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  return formatDate(d);
}

/**
 * M-09 fix: Compute today + yesterday from a single fixed timestamp.
 * Prevents cross-midnight race where todayStr() and yesterdayStr() span different days.
 */
function getStreakDates(): { today: string; yesterday: string } {
  const now = new Date();
  const today = formatDate(now);
  const yd = new Date(now.getTime() - 86400_000);
  return { today, yesterday: formatDate(yd) };
}

// ========================================
// Store
// ========================================
interface LearningState {
  progress: Record<string, ConceptProgress>;
  history: LearningHistory[];
  streak: StreakData;
  stats: LearningStats | null;
  /** Whether we've synced local data to backend at least once this session */
  backendSynced: boolean;

  /** Edge data for prerequisite-based unlocking */
  prereqMap: Map<string, string[]>;
  dependentsMap: Map<string, string[]>;
  /** Concepts that are "recommended" (all prereqs mastered, not yet mastered themselves) */
  recommendedIds: Set<string>;
  /** Most recently unlocked concept IDs (for animation/notification) */
  newlyUnlockedIds: string[];

  // Actions
  /** Initialize edge data from graph for prerequisite tracking */
  initEdges: (edges: PrereqEdge[]) => void;
  /** Mark a concept as "learning" when user starts a session */
  startLearning: (conceptId: string) => void;
  /** Record an assessment result, potentially marking as mastered */
  recordAssessment: (conceptId: string, conceptName: string, score: number, mastered: boolean) => void;
  /** Get status of a single concept */
  getConceptStatus: (conceptId: string) => ConceptStatus;
  /** Check if a concept is "recommended" (prereqs all mastered) */
  isRecommended: (conceptId: string) => boolean;
  /** Compute real stats from progress data + total node count */
  computeStats: (totalConcepts: number) => LearningStats;
  /** Refresh streak based on today's date */
  refreshStreak: () => void;
  /** Clear newly unlocked (after UI has shown notification) */
  clearNewlyUnlocked: () => void;
  /** Import data from a previously exported JSON blob (merge strategy) */
  importData: (data: { progress?: Record<string, ConceptProgress>; history?: LearningHistory[]; streak?: StreakData }) => { imported: number; merged: number };
  /** Completely replace local data (for full restore) */
  replaceData: (data: { progress: Record<string, ConceptProgress>; history: LearningHistory[]; streak: StreakData }) => void;
  /** Sync local data to backend (one-time migration + merge) */
  syncWithBackend: () => Promise<void>;
  /** Switch to a different domain's learning data — reloads progress/history from localStorage */
  switchDomain: (domain: string) => void;
}

// Run migration on first load
migrateLegacyStorage(_activeDomain);

export const useLearningStore = create<LearningState>((set, get) => ({
  progress: loadProgress(),
  history: loadHistory(),
  streak: loadStreak(),
  stats: null,
  backendSynced: false,
  prereqMap: new Map(),
  dependentsMap: new Map(),
  recommendedIds: new Set(),
  newlyUnlockedIds: [],

  initEdges: (edges: PrereqEdge[]) => {
    const prereqMap = buildPrereqMap(edges);
    const dependentsMap = buildDependentsMap(edges);
    // Compute initial recommended set
    const { progress } = get();
    const allTargets = new Set(edges.map((e) => e.target));
    const allSources = new Set(edges.map((e) => e.source));
    const allIds = new Set([...allTargets, ...allSources]);
    const recommended = new Set<string>();
    for (const id of allIds) {
      if (progress[id]?.status === 'mastered') continue;
      if (arePrereqsMet(id, prereqMap, progress)) {
        recommended.add(id);
      }
    }
    set({ prereqMap, dependentsMap, recommendedIds: recommended });
  },

  startLearning: (conceptId) => {
    log.info('startLearning called', { conceptId });
    const { progress, streak } = get();
    const existing = progress[conceptId];
    const now = Date.now();
    // M-09 fix: Use single fixed timestamp for streak dates (prevents cross-midnight race)
    const { today, yesterday } = getStreakDates();

    const updated: ConceptProgress = existing
      ? { ...existing, status: existing.status === 'mastered' ? 'mastered' : 'learning', sessions: existing.sessions + 1, last_learn_at: now }
      : { concept_id: conceptId, status: 'learning', mastery_score: 0, sessions: 1, total_time_sec: 0, last_learn_at: now };

    const newProgress = { ...progress, [conceptId]: updated };
    const saved = saveProgress(newProgress);
    log.info('startLearning saveProgress', { saved, entries: Object.keys(newProgress).length });

    // Update streak
    let newStreak = { ...streak };
    if (streak.lastDate !== today) {
      if (streak.lastDate === yesterday) {
        newStreak.current += 1;
      } else {
        newStreak.current = 1;
      }
      newStreak.lastDate = today;
      newStreak.longest = Math.max(newStreak.longest, newStreak.current);
      saveStreak(newStreak);
    }

    set({ progress: newProgress, streak: newStreak });

    // Async write to backend (fire-and-forget)
    apiStartLearning(conceptId);

    // Supabase-first path for logged-in users (ADR-011)
    if (isLoggedIn()) {
      writeProgressToCloud(updated).then(ok => {
        if (!ok) {
          // Supabase write failed — enqueue for offline retry
          enqueue({ type: 'progress', concept_id: updated.concept_id, data: { ...updated }, created_at: now });
        }
      });
    } else {
      // Anonymous: fire-and-forget sync (if configured)
      syncProgressToCloud(updated);
    }
  },

  recordAssessment: (conceptId, conceptName, score, mastered) => {
    log.info('recordAssessment called', { conceptId, conceptName, score, mastered });
    const { progress, history } = get();
    const existing = progress[conceptId];
    const now = Date.now();

    // Prevent demotion: once mastered, status stays mastered (user is reviewing)
    const wasMastered = existing?.status === 'mastered';
    const nowMastered = mastered || wasMastered;

    const updated: ConceptProgress = {
      concept_id: conceptId,
      status: nowMastered ? 'mastered' : 'learning',
      mastery_score: nowMastered ? Math.max(score, existing?.mastery_score || 0) : score,
      last_score: score,
      sessions: existing?.sessions || 1,
      total_time_sec: existing?.total_time_sec || 0,
      mastered_at: nowMastered ? (existing?.mastered_at || now) : existing?.mastered_at,
      last_learn_at: now,
    };

    const newProgress = { ...progress, [conceptId]: updated };
    const savedP = saveProgress(newProgress);

    const newHistory: LearningHistory[] = [
      ...history,
      { concept_id: conceptId, concept_name: conceptName, score, mastered, timestamp: now },
    ];
    const savedH = saveHistory(newHistory);
    log.info('recordAssessment save', { progress: savedP ? 'OK' : 'FAILED', history: savedH ? 'OK' : 'FAILED', status: updated.status, entries: Object.keys(newProgress).length });

    // Compute newly unlocked concepts if this node was just mastered
    let newlyUnlocked: string[] = [];
    const { dependentsMap, prereqMap, recommendedIds } = get();
    if (mastered && dependentsMap.size > 0) {
      newlyUnlocked = getNewlyUnlocked(conceptId, dependentsMap, prereqMap, newProgress);
      const updated_recommended = new Set(recommendedIds);
      updated_recommended.delete(conceptId);
      for (const uid of newlyUnlocked) {
        updated_recommended.add(uid);
      }
      set({ progress: newProgress, history: newHistory, newlyUnlockedIds: newlyUnlocked, recommendedIds: updated_recommended });
    } else {
      set({ progress: newProgress, history: newHistory });
    }

    // Async write to backend (fire-and-forget)
    apiRecordAssessment(conceptId, conceptName, score, mastered);

    // Supabase-first path for logged-in users (ADR-011)
    if (isLoggedIn()) {
      writeProgressToCloud(updated).then(ok => {
        if (!ok) enqueue({ type: 'progress', concept_id: updated.concept_id, data: { ...updated }, created_at: now });
      });
      writeHistoryToCloud(conceptId, conceptName, score, mastered).then(ok => {
        if (!ok) enqueue({ type: 'history', concept_id: conceptId, concept_name: conceptName, score, mastered, created_at: now });
      });
    } else {
      // Anonymous: fire-and-forget sync (if configured)
      syncProgressToCloud(updated);
      syncHistoryToCloud(conceptId, conceptName, score, mastered);
    }
  },

  getConceptStatus: (conceptId) => {
    const { progress } = get();
    return progress[conceptId]?.status || 'not_started';
  },

  isRecommended: (conceptId) => {
    const { recommendedIds } = get();
    return recommendedIds.has(conceptId);
  },

  computeStats: (totalConcepts) => {
    get().refreshStreak();

    const { progress, streak } = get();
    const entries = Object.values(progress);
    const mastered = entries.filter((p) => p.status === 'mastered').length;
    const learning = entries.filter((p) => p.status === 'learning').length;
    const notStarted = Math.max(0, totalConcepts - mastered - learning);
    const totalTime = entries.reduce((sum, p) => sum + p.total_time_sec, 0);

    const stats: LearningStats = {
      total_concepts: totalConcepts,
      mastered_count: mastered,
      learning_count: learning,
      available_count: notStarted,
      locked_count: 0,
      not_started_count: notStarted,
      total_study_time_sec: totalTime,
      current_streak: streak.current,
      longest_streak: streak.longest,
    };

    set({ stats });
    return stats;
  },

  refreshStreak: () => {
    const { streak } = get();
    const today = todayStr();
    if (streak.lastDate && streak.lastDate !== today) {
      if (streak.lastDate !== yesterdayStr()) {
        // Streak broken: reset current to 0 and update lastDate to prevent repeated resets
        if (streak.current !== 0) {
          const newStreak = { ...streak, current: 0, lastDate: today };
          saveStreak(newStreak);
          set({ streak: newStreak });
        }
      }
    }
  },

  clearNewlyUnlocked: () => {
    set({ newlyUnlockedIds: [] });
  },

  importData: (data) => {
    const { progress: existingProgress, history: existingHistory, streak: existingStreak } = get();
    let imported = 0;
    let merged = 0;

    // Merge progress
    const mergedProgress = { ...existingProgress };
    if (data.progress) {
      for (const [key, val] of Object.entries(data.progress)) {
        if (!isValidProgress(val)) continue;
        const existing = mergedProgress[key];
        if (!existing) {
          mergedProgress[key] = val;
          imported++;
        } else if (val.last_learn_at > existing.last_learn_at) {
          mergedProgress[key] = val;
          merged++;
        }
      }
    }

    // Merge history (deduplicate by concept_id + timestamp)
    const historySet = new Set(existingHistory.map(h => `${h.concept_id}-${h.timestamp}`));
    const mergedHistory = [...existingHistory];
    if (data.history) {
      for (const h of data.history) {
        const key = `${h.concept_id}-${h.timestamp}`;
        if (!historySet.has(key)) {
          mergedHistory.push(h);
          historySet.add(key);
        }
      }
      mergedHistory.sort((a, b) => a.timestamp - b.timestamp);
    }

    // Merge streak (take max)
    let mergedStreak = { ...existingStreak };
    if (data.streak) {
      // Use the streak with the more recent lastDate (not just max)
      const importLastDate = data.streak.lastDate || '';
      const useImported = importLastDate > existingStreak.lastDate;
      mergedStreak = {
        current: useImported ? (data.streak.current || 0) : existingStreak.current,
        longest: Math.max(existingStreak.longest, data.streak.longest || 0),
        lastDate: useImported ? importLastDate : existingStreak.lastDate,
      };
    }

    saveProgress(mergedProgress);
    saveHistory(mergedHistory);
    saveStreak(mergedStreak);
    set({ progress: mergedProgress, history: mergedHistory, streak: mergedStreak });
    return { imported, merged };
  },

  replaceData: (data) => {
    saveProgress(data.progress);
    saveHistory(data.history);
    saveStreak(data.streak);
    set({ progress: data.progress, history: data.history, streak: data.streak });
  },

  syncWithBackend: async () => {
    if (get().backendSynced) return;

    try {
      // Backend SQLite has NO user isolation — all anonymous users share the same DB.
      // Pulling data from backend would merge other users' progress into local storage.
      // Only push local data to backend (for recommendation engine), never pull back.
      const localProgress = get().progress;
      const localHistory = get().history;
      const localStreak = get().streak;

      if (Object.keys(localProgress).length > 0 || localHistory.length > 0) {
        await apiSyncToBackend({
          progress: localProgress,
          history: localHistory,
          streak: localStreak,
        });
      }

      // Skip pull from backend — localStorage is the single source of truth for anonymous users.
      // When Supabase auth is configured (Phase 5), user-specific sync uses supabase-sync.ts instead.
      set({ backendSynced: true });
      log.info('Backend push-only sync complete', { concepts: Object.keys(localProgress).length });
    } catch (err) {
      log.warn('Backend sync failed, using local data', { err: (err as Error).message });
      set({ backendSynced: true }); // Don't retry this session
    }
  },

  switchDomain: (domain: string) => {
    // Run migration for legacy flat keys → first domain (only if needed)
    migrateLegacyStorage(domain);
    // Update active domain for storage operations
    _activeDomain = domain;
    // Reload progress and history from new domain's localStorage
    const progress = loadProgress(domain);
    const history = loadHistory(domain);
    set({
      progress,
      history,
      stats: null,
      backendSynced: false,
      recommendedIds: new Set(),
      newlyUnlockedIds: [],
    });
    log.info('Switched to domain', { domain, concepts: Object.keys(progress).length });
  },
}));

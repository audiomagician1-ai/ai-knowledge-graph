import { create } from 'zustand';
import type { LearningStats, ConceptStatus } from '@akg/shared';
import {
  apiStartLearning, apiRecordAssessment, apiFetchAllProgress,
  apiFetchStats, apiFetchHistory, apiFetchStreak, apiSyncToBackend,
} from '@/lib/api/learning-api';
import { syncProgressToCloud, syncHistoryToCloud } from './supabase-sync';

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
// localStorage persistence
// ========================================
const STORAGE_KEY = 'akg-learning';
const HISTORY_KEY = 'akg-learning-history';
const STREAK_KEY = 'akg-streak';

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

function loadProgress(): Record<string, ConceptProgress> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed: PersistedData = JSON.parse(raw);
      const progress = parsed.progress || {};
      // Validate entries, skip corrupted ones
      const validated: Record<string, ConceptProgress> = {};
      for (const [key, val] of Object.entries(progress)) {
        if (isValidProgress(val)) {
          validated[key] = val;
        } else {
          console.warn(`[learning] Skipped corrupted progress entry: ${key}`);
        }
      }
      return validated;
    }
  } catch (e) {
    console.warn('[learning] Failed to load progress from localStorage:', e);
  }
  return {};
}

function saveProgress(progress: Record<string, ConceptProgress>) {
  try {
    const data: PersistedData = { progress };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch { /* ignore */ }
}

function loadHistory(): LearningHistory[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
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
    console.warn('[learning] Failed to load history from localStorage:', e);
  }
  return [];
}

function saveHistory(history: LearningHistory[]) {
  try {
    // Keep last 100 entries
    const trimmed = history.slice(-100);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(trimmed));
  } catch { /* ignore */ }
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

function saveStreak(streak: StreakData) {
  try {
    localStorage.setItem(STREAK_KEY, JSON.stringify(streak));
  } catch { /* ignore */ }
}

/** Get today's date string in local timezone (YYYY-MM-DD) */
function todayStr(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

/** Get yesterday's date string in local timezone */
function yesterdayStr(): string {
  const d = new Date();
  d.setDate(d.getDate() - 1);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
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
}

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
    const { progress, streak } = get();
    const existing = progress[conceptId];
    const now = Date.now();
    const today = todayStr();

    const updated: ConceptProgress = existing
      ? { ...existing, status: existing.status === 'mastered' ? 'mastered' : 'learning', sessions: existing.sessions + 1, last_learn_at: now }
      : { concept_id: conceptId, status: 'learning', mastery_score: 0, sessions: 1, total_time_sec: 0, last_learn_at: now };

    const newProgress = { ...progress, [conceptId]: updated };
    saveProgress(newProgress);

    // Update streak
    let newStreak = { ...streak };
    if (streak.lastDate !== today) {
      if (streak.lastDate === yesterdayStr()) {
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
    // Async write to Supabase cloud (fire-and-forget, logged-in only)
    syncProgressToCloud(updated);
  },

  recordAssessment: (conceptId, conceptName, score, mastered) => {
    const { progress, history } = get();
    const existing = progress[conceptId];
    const now = Date.now();

    const updated: ConceptProgress = {
      concept_id: conceptId,
      status: mastered ? 'mastered' : 'learning',
      mastery_score: mastered ? Math.max(score, existing?.mastery_score || 0) : score,
      last_score: score,
      sessions: existing?.sessions || 1,
      total_time_sec: existing?.total_time_sec || 0,
      mastered_at: mastered ? (existing?.mastered_at || now) : undefined,
      last_learn_at: now,
    };

    const newProgress = { ...progress, [conceptId]: updated };
    saveProgress(newProgress);

    const newHistory: LearningHistory[] = [
      ...history,
      { concept_id: conceptId, concept_name: conceptName, score, mastered, timestamp: now },
    ];
    saveHistory(newHistory);

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
    // Async write to Supabase cloud (fire-and-forget, logged-in only)
    syncProgressToCloud(updated);
    syncHistoryToCloud(conceptId, conceptName, score, mastered);
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
        const newStreak = { ...streak, current: 0 };
        saveStreak(newStreak);
        set({ streak: newStreak });
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
      // 1. Push local data to backend (in case backend DB is empty/new)
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

      // 2. Pull merged data from backend (backend has the authoritative state now)
      const [backendProgress, backendHistory, backendStreak] = await Promise.all([
        apiFetchAllProgress(),
        apiFetchHistory(100),
        apiFetchStreak(),
      ]);

      // 3. Merge: backend data takes priority for progress, merge into local format
      const mergedProgress: Record<string, ConceptProgress> = { ...localProgress };
      for (const [cid, bp] of Object.entries(backendProgress)) {
        const local = mergedProgress[cid];
        const backendItem = bp as any;
        // Backend has newer or equal data → use it
        if (!local || (backendItem.last_learn_at && backendItem.last_learn_at >= (local.last_learn_at || 0))) {
          mergedProgress[cid] = {
            concept_id: cid,
            status: backendItem.status || 'not_started',
            mastery_score: backendItem.mastery_score || 0,
            last_score: backendItem.last_score,
            sessions: backendItem.sessions || 0,
            total_time_sec: backendItem.total_time_sec || 0,
            mastered_at: backendItem.mastered_at,
            last_learn_at: backendItem.last_learn_at || 0,
          };
        }
      }

      // Merge history (deduplicate by timestamp+concept_id)
      const historySet = new Set(localHistory.map(h => `${h.concept_id}-${h.timestamp}`));
      const mergedHistory = [...localHistory];
      for (const bh of (backendHistory as any[])) {
        const key = `${bh.concept_id}-${bh.timestamp}`;
        if (!historySet.has(key)) {
          mergedHistory.push({
            concept_id: bh.concept_id,
            concept_name: bh.concept_name,
            score: bh.score,
            mastered: !!bh.mastered,
            timestamp: bh.timestamp,
          });
          historySet.add(key);
        }
      }
      mergedHistory.sort((a, b) => a.timestamp - b.timestamp);

      // Merge streak (take max)
      let mergedStreak = { ...localStreak };
      if (backendStreak) {
        // Use the streak with the more recent lastDate (not just max)
        const backendLastDate = backendStreak.last_date || '';
        const useBackend = backendLastDate > localStreak.lastDate;
        mergedStreak = {
          current: useBackend ? (backendStreak.current_streak || 0) : localStreak.current,
          longest: Math.max(localStreak.longest, backendStreak.longest_streak || 0),
          lastDate: useBackend ? backendLastDate : localStreak.lastDate,
        };
      }

      // 4. Save merged data locally
      saveProgress(mergedProgress);
      saveHistory(mergedHistory);
      saveStreak(mergedStreak);

      set({
        progress: mergedProgress,
        history: mergedHistory,
        streak: mergedStreak,
        backendSynced: true,
      });

      console.log('[learning] Backend sync complete:', Object.keys(mergedProgress).length, 'concepts');
    } catch (err) {
      console.warn('[learning] Backend sync failed, using local data:', err);
      set({ backendSynced: true }); // Don't retry this session
    }
  },
}));

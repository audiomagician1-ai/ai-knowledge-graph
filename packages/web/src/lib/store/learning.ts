import { create } from 'zustand';
import type { LearningStats, ConceptStatus } from '@akg/shared';

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

function loadProgress(): Record<string, ConceptProgress> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed: PersistedData = JSON.parse(raw);
      return parsed.progress || {};
    }
  } catch { /* ignore */ }
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
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
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

  // Actions
  /** Mark a concept as "learning" when user starts a session */
  startLearning: (conceptId: string) => void;
  /** Record an assessment result, potentially marking as mastered */
  recordAssessment: (conceptId: string, conceptName: string, score: number, mastered: boolean) => void;
  /** Get status of a single concept */
  getConceptStatus: (conceptId: string) => ConceptStatus;
  /** Compute real stats from progress data + total node count */
  computeStats: (totalConcepts: number) => LearningStats;
  /** Refresh streak based on today's date */
  refreshStreak: () => void;
}

export const useLearningStore = create<LearningState>((set, get) => ({
  progress: loadProgress(),
  history: loadHistory(),
  streak: loadStreak(),
  stats: null,

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
      sessions: existing?.sessions || 1, // inherit; at least 1 since we're assessing
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

    set({ progress: newProgress, history: newHistory });
  },

  getConceptStatus: (conceptId) => {
    const { progress } = get();
    return progress[conceptId]?.status || 'not_started';
  },

  computeStats: (totalConcepts) => {
    // Auto-refresh streak on each stats computation
    get().refreshStreak();

    const { progress, streak } = get();
    const entries = Object.values(progress);
    const mastered = entries.filter((p) => p.status === 'mastered').length;
    const learning = entries.filter((p) => p.status === 'learning').length;
    const notStarted = totalConcepts - mastered - learning;
    const totalTime = entries.reduce((sum, p) => sum + p.total_time_sec, 0);

    const stats: LearningStats = {
      total_concepts: totalConcepts,
      mastered_count: mastered,
      learning_count: learning,
      available_count: notStarted, // no lock system — available = not_started
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
    // Only act if there's a previous date and it's not today
    if (streak.lastDate && streak.lastDate !== today) {
      if (streak.lastDate !== yesterdayStr()) {
        // Streak broken — last activity was before yesterday
        const newStreak = { ...streak, current: 0 };
        saveStreak(newStreak);
        set({ streak: newStreak });
      }
    }
  },
}));

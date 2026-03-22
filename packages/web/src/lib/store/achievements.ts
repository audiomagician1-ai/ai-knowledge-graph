/**
 * Achievement Store — Zustand store for gamification achievements.
 *
 * Manages achievement catalog, unlock status, progress tracking, and toast notifications.
 * Communicates with backend via learning-api.ts.
 */
import { create } from 'zustand';
import {
  apiFetchAchievements,
  apiFetchRecentAchievements,
  apiMarkAchievementsSeen,
  type Achievement,
  type AchievementsResponse,
} from '@/lib/api/learning-api';
import { useToastStore } from '@/lib/store/toast';

interface AchievementState {
  /** All achievements with status/progress */
  achievements: Achievement[];
  /** Summary counts */
  summary: AchievementsResponse['summary'] | null;
  /** Whether initial load is in progress */
  loading: boolean;
  /** Unseen achievement count (for badge) */
  unseenCount: number;

  /** Fetch full achievement catalog from backend */
  fetchAchievements: () => Promise<void>;
  /** Check for newly unlocked achievements and show toast notifications */
  checkNewAchievements: () => Promise<void>;
  /** Mark all unseen achievements as seen */
  markAllSeen: () => Promise<void>;
}

export const useAchievementStore = create<AchievementState>((set, get) => ({
  achievements: [],
  summary: null,
  loading: false,
  unseenCount: 0,

  fetchAchievements: async () => {
    set({ loading: true });
    try {
      const data = await apiFetchAchievements();
      if (data) {
        set({
          achievements: data.achievements,
          summary: data.summary,
          unseenCount: data.achievements.filter(a => a.unlocked && !a.seen).length,
        });
      }
    } finally {
      set({ loading: false });
    }
  },

  checkNewAchievements: async () => {
    const data = await apiFetchRecentAchievements();
    if (data && data.unseen_count > 0) {
      set({ unseenCount: data.unseen_count });
      // Show toast for each newly unlocked achievement
      const { addToast } = useToastStore.getState();
      for (const ach of data.achievements) {
        addToast('success', `${ach.icon} 成就解锁: ${ach.name}`, 5000);
      }
    }
  },

  markAllSeen: async () => {
    const { achievements } = get();
    const unseenKeys = achievements
      .filter(a => a.unlocked && !a.seen)
      .map(a => a.key);
    if (unseenKeys.length === 0) return;

    await apiMarkAchievementsSeen(unseenKeys);
    set((state) => ({
      unseenCount: 0,
      achievements: state.achievements.map(a =>
        a.unlocked && !a.seen ? { ...a, seen: true } : a
      ),
    }));
  },
}));

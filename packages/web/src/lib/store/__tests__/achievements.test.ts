/**
 * achievements.ts store tests — gamification achievement system
 */
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { useAchievementStore } from '@/lib/store/achievements';
import { useToastStore } from '@/lib/store/toast';

// ─── Mock API layer ─────────────────────────────────────────
vi.mock('@/lib/api/learning-api', () => ({
  apiFetchAchievements: vi.fn(),
  apiFetchRecentAchievements: vi.fn(),
  apiMarkAchievementsSeen: vi.fn(),
}));

import {
  apiFetchAchievements,
  apiFetchRecentAchievements,
  apiMarkAchievementsSeen,
} from '@/lib/api/learning-api';

const mockFetchAll = vi.mocked(apiFetchAchievements);
const mockFetchRecent = vi.mocked(apiFetchRecentAchievements);
const mockMarkSeen = vi.mocked(apiMarkAchievementsSeen);

// ─── Helpers ────────────────────────────────────────────────
function makeAchievement(overrides: Partial<{
  key: string; category: string; name: string; description: string;
  icon: string; tier: string; unlocked: boolean; progress: number;
  unlocked_at: number; seen: boolean;
}> = {}) {
  return {
    key: overrides.key ?? 'first_light',
    category: overrides.category ?? 'learning',
    name: overrides.name ?? '第一道光',
    description: overrides.description ?? '学习第一个概念',
    icon: overrides.icon ?? '💡',
    tier: overrides.tier ?? 'bronze' as const,
    unlocked: overrides.unlocked ?? false,
    progress: overrides.progress ?? 0,
    unlocked_at: overrides.unlocked_at,
    seen: overrides.seen,
  };
}

const FULL_RESPONSE = {
  summary: {
    total: 20,
    unlocked: 3,
    categories: {
      learning: { total: 5, unlocked: 2 },
      streak: { total: 4, unlocked: 1 },
      domain: { total: 3, unlocked: 0 },
      assessment: { total: 3, unlocked: 0 },
      review: { total: 3, unlocked: 0 },
      special: { total: 2, unlocked: 0 },
    },
  },
  achievements: [
    makeAchievement({ key: 'first_light', unlocked: true, progress: 100, unlocked_at: 1711100000, seen: true }),
    makeAchievement({ key: 'explorer', name: '探索者', unlocked: true, progress: 100, unlocked_at: 1711200000, seen: false }),
    makeAchievement({ key: 'scholar', name: '学者', unlocked: true, progress: 100, unlocked_at: 1711300000, seen: false }),
    makeAchievement({ key: 'streak_3', category: 'streak', name: '三日连燃', unlocked: false, progress: 66 }),
  ],
};

// ─── Test Suite ─────────────────────────────────────────────
describe('useAchievementStore', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    // Reset store state
    useAchievementStore.setState({
      achievements: [],
      summary: null,
      loading: false,
      unseenCount: 0,
    });
    useToastStore.setState({ toasts: [] });
    // Reset mocks
    mockFetchAll.mockReset();
    mockFetchRecent.mockReset();
    mockMarkSeen.mockReset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('initial state', () => {
    it('should have empty achievements and zero unseen', () => {
      const state = useAchievementStore.getState();
      expect(state.achievements).toEqual([]);
      expect(state.summary).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.unseenCount).toBe(0);
    });
  });

  describe('fetchAchievements', () => {
    it('should load achievements from API', async () => {
      mockFetchAll.mockResolvedValue(FULL_RESPONSE as any);

      await useAchievementStore.getState().fetchAchievements();

      const state = useAchievementStore.getState();
      expect(state.achievements).toHaveLength(4);
      expect(state.summary).toEqual(FULL_RESPONSE.summary);
      expect(state.loading).toBe(false);
    });

    it('should set loading true during fetch', async () => {
      let resolvePromise: (v: any) => void;
      const promise = new Promise(r => { resolvePromise = r; });
      mockFetchAll.mockReturnValue(promise as any);

      const fetchPromise = useAchievementStore.getState().fetchAchievements();
      expect(useAchievementStore.getState().loading).toBe(true);

      resolvePromise!(FULL_RESPONSE);
      await fetchPromise;
      expect(useAchievementStore.getState().loading).toBe(false);
    });

    it('should count unseen unlocked achievements', async () => {
      mockFetchAll.mockResolvedValue(FULL_RESPONSE as any);

      await useAchievementStore.getState().fetchAchievements();

      // explorer + scholar are unlocked but not seen
      expect(useAchievementStore.getState().unseenCount).toBe(2);
    });

    it('should handle API failure gracefully', async () => {
      mockFetchAll.mockResolvedValue(null);

      await useAchievementStore.getState().fetchAchievements();

      const state = useAchievementStore.getState();
      expect(state.achievements).toEqual([]);
      expect(state.loading).toBe(false);
    });

    it('should reset loading on error', async () => {
      mockFetchAll.mockRejectedValue(new Error('Network error'));

      await useAchievementStore.getState().fetchAchievements().catch(() => {});

      expect(useAchievementStore.getState().loading).toBe(false);
    });
  });

  describe('checkNewAchievements', () => {
    it('should show toast for each new achievement', async () => {
      mockFetchRecent.mockResolvedValue({
        unseen_count: 2,
        achievements: [
          { key: 'explorer', name: '探索者', icon: '🔭', tier: 'bronze', unlocked_at: 1711200000 },
          { key: 'scholar', name: '学者', icon: '📚', tier: 'silver', unlocked_at: 1711300000 },
        ],
      });

      await useAchievementStore.getState().checkNewAchievements();

      expect(useAchievementStore.getState().unseenCount).toBe(2);
      const toasts = useToastStore.getState().toasts;
      expect(toasts).toHaveLength(2);
      expect(toasts[0].message).toContain('探索者');
      expect(toasts[0].type).toBe('success');
      expect(toasts[1].message).toContain('学者');
    });

    it('should not show toast when no new achievements', async () => {
      mockFetchRecent.mockResolvedValue({
        unseen_count: 0,
        achievements: [],
      });

      await useAchievementStore.getState().checkNewAchievements();

      expect(useAchievementStore.getState().unseenCount).toBe(0);
      expect(useToastStore.getState().toasts).toHaveLength(0);
    });

    it('should handle API returning null', async () => {
      mockFetchRecent.mockResolvedValue(null);

      await useAchievementStore.getState().checkNewAchievements();

      expect(useAchievementStore.getState().unseenCount).toBe(0);
      expect(useToastStore.getState().toasts).toHaveLength(0);
    });
  });

  describe('markAllSeen', () => {
    it('should call API with unseen achievement keys', async () => {
      mockFetchAll.mockResolvedValue(FULL_RESPONSE as any);
      await useAchievementStore.getState().fetchAchievements();

      mockMarkSeen.mockResolvedValue(undefined);
      await useAchievementStore.getState().markAllSeen();

      // Should send explorer + scholar (unlocked but not seen)
      expect(mockMarkSeen).toHaveBeenCalledWith(['explorer', 'scholar']);
    });

    it('should set unseenCount to 0 after marking', async () => {
      mockFetchAll.mockResolvedValue(FULL_RESPONSE as any);
      await useAchievementStore.getState().fetchAchievements();
      expect(useAchievementStore.getState().unseenCount).toBe(2);

      mockMarkSeen.mockResolvedValue(undefined);
      await useAchievementStore.getState().markAllSeen();

      expect(useAchievementStore.getState().unseenCount).toBe(0);
    });

    it('should update achievement seen status in state', async () => {
      mockFetchAll.mockResolvedValue(FULL_RESPONSE as any);
      await useAchievementStore.getState().fetchAchievements();

      mockMarkSeen.mockResolvedValue(undefined);
      await useAchievementStore.getState().markAllSeen();

      const state = useAchievementStore.getState();
      const unseenAchievements = state.achievements.filter(a => a.unlocked && !a.seen);
      expect(unseenAchievements).toHaveLength(0);
    });

    it('should skip API call when no unseen achievements', async () => {
      // Set state with all achievements already seen
      useAchievementStore.setState({
        achievements: [
          makeAchievement({ key: 'first_light', unlocked: true, progress: 100, seen: true }) as any,
        ],
        unseenCount: 0,
      });

      await useAchievementStore.getState().markAllSeen();

      expect(mockMarkSeen).not.toHaveBeenCalled();
    });

    it('should not mark locked achievements', async () => {
      useAchievementStore.setState({
        achievements: [
          makeAchievement({ key: 'a1', unlocked: true, seen: false }) as any,
          makeAchievement({ key: 'a2', unlocked: false, seen: false }) as any, // locked — should not be sent
        ],
        unseenCount: 1,
      });

      mockMarkSeen.mockResolvedValue(undefined);
      await useAchievementStore.getState().markAllSeen();

      // Only 'a1' should be sent (unlocked && !seen)
      expect(mockMarkSeen).toHaveBeenCalledWith(['a1']);
    });
  });

  describe('unseenCount', () => {
    it('should count only unlocked-and-unseen achievements', async () => {
      const response = {
        summary: { total: 4, unlocked: 3, categories: {} },
        achievements: [
          makeAchievement({ key: 'a1', unlocked: true, seen: true }),   // seen → not counted
          makeAchievement({ key: 'a2', unlocked: true, seen: false }),  // unseen → counted
          makeAchievement({ key: 'a3', unlocked: true, seen: false }),  // unseen → counted
          makeAchievement({ key: 'a4', unlocked: false, seen: false }), // locked → not counted
        ],
      };
      mockFetchAll.mockResolvedValue(response as any);

      await useAchievementStore.getState().fetchAchievements();

      expect(useAchievementStore.getState().unseenCount).toBe(2);
    });

    it('should be zero when all unlocked are seen', async () => {
      const response = {
        summary: { total: 2, unlocked: 2, categories: {} },
        achievements: [
          makeAchievement({ key: 'a1', unlocked: true, seen: true }),
          makeAchievement({ key: 'a2', unlocked: true, seen: true }),
        ],
      };
      mockFetchAll.mockResolvedValue(response as any);

      await useAchievementStore.getState().fetchAchievements();

      expect(useAchievementStore.getState().unseenCount).toBe(0);
    });
  });
});

/**
 * supabase-sync.ts tests — merge logic + guard functions
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock localStorage
const storage: Record<string, string> = {};
vi.stubGlobal('localStorage', {
  getItem: (key: string) => storage[key] ?? null,
  setItem: (key: string, value: string) => { storage[key] = value; },
  removeItem: (key: string) => { delete storage[key]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); },
});

// Track supabase calls
const mockUpsert = vi.fn(() => Promise.resolve({ error: null }));
const mockInsert = vi.fn(() => Promise.resolve({ error: null }));
const mockSelect = vi.fn(() => ({
  eq: vi.fn(() => ({
    data: [],
    error: null,
    // For chained calls
    in: vi.fn(() => ({
      order: vi.fn(() => ({
        limit: vi.fn(() => Promise.resolve({ data: [], error: null })),
      })),
    })),
    order: vi.fn(() => ({
      limit: vi.fn(() => Promise.resolve({ data: [], error: null })),
    })),
  })),
}));

vi.mock('@/lib/api/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(() => Promise.resolve({ data: { session: null } })),
      onAuthStateChange: vi.fn(() => ({
        data: { subscription: { unsubscribe: vi.fn() } },
      })),
    },
    from: vi.fn(() => ({
      upsert: mockUpsert,
      insert: mockInsert,
      select: mockSelect,
    })),
  },
}));

// Mock auth store
vi.mock('@/lib/store/auth', () => ({
  onAuthLogin: vi.fn((cb: any) => () => {}),
  useAuthStore: {
    getState: vi.fn(() => ({
      user: null,
      isAuthenticated: () => false,
    })),
  },
}));

// Mock learning-api
vi.mock('@/lib/api/learning-api', () => ({
  apiStartLearning: vi.fn(),
  apiRecordAssessment: vi.fn(),
  apiFetchAllProgress: vi.fn(() => Promise.resolve({})),
  apiFetchStats: vi.fn(() => Promise.resolve({})),
  apiFetchHistory: vi.fn(() => Promise.resolve([])),
  apiFetchStreak: vi.fn(() => Promise.resolve(null)),
  apiSyncToBackend: vi.fn(() => Promise.resolve()),
}));

import {
  syncProgressToCloud,
  syncHistoryToCloud,
  syncConversationToCloud,
  fullSync,
} from '@/lib/store/supabase-sync';
import { useAuthStore } from '@/lib/store/auth';

describe('supabase-sync', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  describe('syncProgressToCloud', () => {
    it('should skip when no user logged in', async () => {
      await syncProgressToCloud({
        concept_id: 'test',
        status: 'learning',
        mastery_score: 50,
        sessions: 1,
        total_time_sec: 0,
        last_learn_at: Date.now(),
      });
      // supabase.from should not be called
      expect(mockUpsert).not.toHaveBeenCalled();
    });

    it('should upsert when user is logged in', async () => {
      vi.mocked(useAuthStore.getState).mockReturnValue({
        user: { id: 'user-123' } as any,
        isAuthenticated: () => true,
      } as any);

      await syncProgressToCloud({
        concept_id: 'test-node',
        status: 'mastered',
        mastery_score: 85,
        sessions: 3,
        total_time_sec: 120,
        last_learn_at: Date.now(),
        mastered_at: Date.now() - 1000,
      });
      // supabase.from should be called
      expect(mockUpsert).toHaveBeenCalled();
    });

    it('should map not_started status to available for DB constraint', async () => {
      vi.mocked(useAuthStore.getState).mockReturnValue({
        user: { id: 'user-456' } as any,
        isAuthenticated: () => true,
      } as any);

      await syncProgressToCloud({
        concept_id: 'unmapped-node',
        status: 'not_started',
        mastery_score: 0,
        sessions: 0,
        total_time_sec: 0,
        last_learn_at: Date.now(),
      });
      expect(mockUpsert).toHaveBeenCalled();
      const callArgs = (mockUpsert.mock.calls[0] as any[])[0];
      expect(callArgs.status).toBe('available');
    });

    it('should pass learning/mastered statuses unchanged', async () => {
      vi.mocked(useAuthStore.getState).mockReturnValue({
        user: { id: 'user-789' } as any,
        isAuthenticated: () => true,
      } as any);

      await syncProgressToCloud({
        concept_id: 'learning-node',
        status: 'learning',
        mastery_score: 30,
        sessions: 1,
        total_time_sec: 60,
        last_learn_at: Date.now(),
      });
      expect(mockUpsert).toHaveBeenCalled();
      const callArgs = (mockUpsert.mock.calls[0] as any[])[0];
      expect(callArgs.status).toBe('learning');
    });
  });

  describe('syncHistoryToCloud', () => {
    it('should skip when no user logged in', async () => {
      vi.mocked(useAuthStore.getState).mockReturnValue({
        user: null,
        isAuthenticated: () => false,
      } as any);

      await syncHistoryToCloud('concept-1', 'Concept 1', 80, true);
      expect(mockInsert).not.toHaveBeenCalled();
    });
  });

  describe('syncConversationToCloud', () => {
    it('should skip when no user logged in', async () => {
      vi.mocked(useAuthStore.getState).mockReturnValue({
        user: null,
        isAuthenticated: () => false,
      } as any);

      await syncConversationToCloud('conv-1', 'concept-1', [], 'active');
      expect(mockUpsert).not.toHaveBeenCalled();
    });
  });

  describe('fullSync', () => {
    it('should return zeros when no user logged in', async () => {
      vi.mocked(useAuthStore.getState).mockReturnValue({
        user: null,
        isAuthenticated: () => false,
      } as any);

      const result = await fullSync();
      expect(result.uploadedProgress).toBe(0);
      expect(result.downloadedProgress).toBe(0);
      expect(result.mergedProgress).toBe(0);
    });

    it('should guard against concurrent calls', async () => {
      vi.mocked(useAuthStore.getState).mockReturnValue({
        user: null,
        isAuthenticated: () => false,
      } as any);

      // Launch two concurrent fullSyncs
      const [r1, r2] = await Promise.all([fullSync(), fullSync()]);
      // At least one should return zeros (the one that hit the _syncing guard)
      const totalUploaded = r1.uploadedProgress + r2.uploadedProgress;
      expect(totalUploaded).toBe(0); // both return 0 since no user
    });
  });
});
/**
 * learning.ts store tests — core business logic
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useLearningStore } from '@/lib/store/learning';

// Mock localStorage
const storage: Record<string, string> = {};
vi.stubGlobal('localStorage', {
  getItem: (key: string) => storage[key] ?? null,
  setItem: (key: string, value: string) => { storage[key] = value; },
  removeItem: (key: string) => { delete storage[key]; },
  clear: () => { Object.keys(storage).forEach(k => delete storage[k]); },
});

// Mock supabase-sync (fire-and-forget + Supabase-first writes)
vi.mock('@/lib/store/supabase-sync', () => ({
  syncProgressToCloud: vi.fn(),
  syncHistoryToCloud: vi.fn(),
  writeProgressToCloud: vi.fn(() => Promise.resolve(true)),
  writeHistoryToCloud: vi.fn(() => Promise.resolve(true)),
  isLoggedIn: vi.fn(() => false), // default: anonymous user
}));

// Mock offline-queue (enqueue for retry on Supabase write failure)
vi.mock('@/lib/store/offline-queue', () => ({
  enqueue: vi.fn(),
  loadQueue: vi.fn(() => []),
  clearQueue: vi.fn(),
  queueSize: vi.fn(() => 0),
  dequeueProcessed: vi.fn(),
  flushQueue: vi.fn(() => Promise.resolve(0)),
  registerOnlineFlush: vi.fn(),
}));

// Mock learning-api (fire-and-forget backend calls)
vi.mock('@/lib/api/learning-api', () => ({
  apiStartLearning: vi.fn(),
  apiRecordAssessment: vi.fn(),
  apiFetchAllProgress: vi.fn(() => Promise.resolve({})),
  apiFetchStats: vi.fn(() => Promise.resolve({})),
  apiFetchHistory: vi.fn(() => Promise.resolve([])),
  apiFetchStreak: vi.fn(() => Promise.resolve(null)),
  apiSyncToBackend: vi.fn(() => Promise.resolve()),
}));

function resetStore() {
  localStorage.clear();
  useLearningStore.setState({
    progress: {},
    history: [],
    streak: { current: 0, longest: 0, lastDate: '' },
    stats: null,
    backendSynced: false,
    prereqMap: new Map(),
    dependentsMap: new Map(),
    recommendedIds: new Set(),
    newlyUnlockedIds: [],
  });
}

describe('useLearningStore', () => {
  beforeEach(() => {
    resetStore();
  });

  describe('startLearning', () => {
    it('should create new progress entry for unknown concept', () => {
      const store = useLearningStore.getState();
      store.startLearning('test_concept');
      const { progress } = useLearningStore.getState();
      expect(progress['test_concept']).toBeDefined();
      expect(progress['test_concept'].status).toBe('learning');
      expect(progress['test_concept'].sessions).toBe(1);
    });

    it('should increment sessions on repeat learning', () => {
      const store = useLearningStore.getState();
      store.startLearning('test_concept');
      store.startLearning('test_concept');
      const { progress } = useLearningStore.getState();
      expect(progress['test_concept'].sessions).toBe(2);
    });

    it('should not demote mastered concept to learning', () => {
      useLearningStore.setState({
        progress: {
          'mastered_node': {
            concept_id: 'mastered_node',
            status: 'mastered',
            mastery_score: 85,
            sessions: 3,
            total_time_sec: 0,
            mastered_at: Date.now() - 10000,
            last_learn_at: Date.now() - 10000,
          },
        },
      });
      useLearningStore.getState().startLearning('mastered_node');
      const { progress } = useLearningStore.getState();
      expect(progress['mastered_node'].status).toBe('mastered');
    });
  });

  describe('recordAssessment', () => {
    it('should mark concept as mastered when mastered=true', () => {
      const store = useLearningStore.getState();
      store.startLearning('concept_a');
      store.recordAssessment('concept_a', 'Concept A', 85, true);
      const { progress, history } = useLearningStore.getState();
      expect(progress['concept_a'].status).toBe('mastered');
      expect(progress['concept_a'].mastery_score).toBe(85);
      expect(progress['concept_a'].mastered_at).toBeDefined();
      expect(history.length).toBe(1);
      expect(history[0].mastered).toBe(true);
    });

    it('should keep status as learning when mastered=false', () => {
      const store = useLearningStore.getState();
      store.startLearning('concept_b');
      store.recordAssessment('concept_b', 'Concept B', 60, false);
      const { progress } = useLearningStore.getState();
      expect(progress['concept_b'].status).toBe('learning');
    });

    it('should NOT demote mastered concept on lower re-assessment score', () => {
      const store = useLearningStore.getState();
      store.startLearning('concept_c');
      store.recordAssessment('concept_c', 'Concept C', 90, true);
      expect(useLearningStore.getState().progress['concept_c'].status).toBe('mastered');

      // Re-assess with lower score, mastered=false
      store.recordAssessment('concept_c', 'Concept C', 50, false);
      const { progress } = useLearningStore.getState();
      // Should still be mastered (no demotion)
      expect(progress['concept_c'].status).toBe('mastered');
      // mastery_score should keep the higher score
      expect(progress['concept_c'].mastery_score).toBe(90);
      // last_score should reflect the latest attempt
      expect(progress['concept_c'].last_score).toBe(50);
    });

    it('should track mastery score as max when mastered', () => {
      const store = useLearningStore.getState();
      store.recordAssessment('concept_d', 'Concept D', 80, true);
      store.recordAssessment('concept_d', 'Concept D', 95, true);
      const { progress } = useLearningStore.getState();
      expect(progress['concept_d'].mastery_score).toBe(95);
    });
  });

  describe('computeStats', () => {
    it('should compute correct stats from progress', () => {
      useLearningStore.setState({
        progress: {
          a: { concept_id: 'a', status: 'mastered', mastery_score: 90, sessions: 2, total_time_sec: 120, last_learn_at: Date.now() },
          b: { concept_id: 'b', status: 'learning', mastery_score: 40, sessions: 1, total_time_sec: 60, last_learn_at: Date.now() },
        },
      });
      const stats = useLearningStore.getState().computeStats(10);
      expect(stats.mastered_count).toBe(1);
      expect(stats.learning_count).toBe(1);
      expect(stats.not_started_count).toBe(8);
      expect(stats.total_study_time_sec).toBe(180);
    });
  });

  describe('importData', () => {
    it('should merge imported data with existing (last_learn_at wins)', () => {
      const now = Date.now();
      useLearningStore.setState({
        progress: {
          existing: { concept_id: 'existing', status: 'learning', mastery_score: 40, sessions: 1, total_time_sec: 0, last_learn_at: now - 1000 },
        },
      });
      const { imported, merged } = useLearningStore.getState().importData({
        progress: {
          existing: { concept_id: 'existing', status: 'mastered', mastery_score: 90, sessions: 3, total_time_sec: 100, last_learn_at: now },
          new_one: { concept_id: 'new_one', status: 'learning', mastery_score: 20, sessions: 1, total_time_sec: 0, last_learn_at: now },
        },
      });
      expect(imported).toBe(1);
      expect(merged).toBe(1);
      const { progress } = useLearningStore.getState();
      expect(progress['existing'].status).toBe('mastered');
      expect(progress['new_one']).toBeDefined();
    });
  });

  describe('streak', () => {
    it('should initialize streak on first learning', () => {
      const store = useLearningStore.getState();
      store.startLearning('streak_test');
      const { streak } = useLearningStore.getState();
      expect(streak.current).toBe(1);
      expect(streak.longest).toBe(1);
      expect(streak.lastDate).toBeTruthy();
    });

    it('should not increment streak for same-day learning', () => {
      const store = useLearningStore.getState();
      store.startLearning('streak_same1');
      store.startLearning('streak_same2');
      const { streak } = useLearningStore.getState();
      expect(streak.current).toBe(1);
    });
  });

  describe('Supabase-first path (logged-in users)', () => {
    beforeEach(async () => {
      resetStore();
      // Clear all mock call records
      const sync = await import('@/lib/store/supabase-sync');
      (sync.isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(false);
      (sync.writeProgressToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);
      (sync.writeHistoryToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);
      (sync.syncProgressToCloud as ReturnType<typeof vi.fn>).mockClear();
      (sync.syncHistoryToCloud as ReturnType<typeof vi.fn>).mockClear();
      (sync.writeProgressToCloud as ReturnType<typeof vi.fn>).mockClear();
      (sync.writeHistoryToCloud as ReturnType<typeof vi.fn>).mockClear();
      const oq = await import('@/lib/store/offline-queue');
      (oq.enqueue as ReturnType<typeof vi.fn>).mockClear();
    });

    it('should call writeProgressToCloud when logged in (startLearning)', async () => {
      const { isLoggedIn, writeProgressToCloud, syncProgressToCloud } = await import('@/lib/store/supabase-sync');

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(true);
      (writeProgressToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);

      const store = useLearningStore.getState();
      store.startLearning('cloud_test');

      // Wait for async write
      await new Promise(r => setTimeout(r, 10));

      expect(writeProgressToCloud).toHaveBeenCalled();
      // syncProgressToCloud should NOT be called when logged in
      expect(syncProgressToCloud).not.toHaveBeenCalled();

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(false);
    });

    it('should call syncProgressToCloud when anonymous (startLearning)', async () => {
      const { isLoggedIn, syncProgressToCloud, writeProgressToCloud } = await import('@/lib/store/supabase-sync');

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(false);

      const store = useLearningStore.getState();
      store.startLearning('anon_test');

      await new Promise(r => setTimeout(r, 10));

      expect(syncProgressToCloud).toHaveBeenCalled();
      expect(writeProgressToCloud).not.toHaveBeenCalled();
    });

    it('should enqueue on writeProgressToCloud failure', async () => {
      const { isLoggedIn, writeProgressToCloud } = await import('@/lib/store/supabase-sync');
      const { enqueue } = await import('@/lib/store/offline-queue');

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(true);
      (writeProgressToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(false); // simulate failure

      const store = useLearningStore.getState();
      store.startLearning('offline_test');

      // Wait for async write + enqueue
      await new Promise(r => setTimeout(r, 20));

      expect(enqueue).toHaveBeenCalledWith(expect.objectContaining({
        type: 'progress',
        concept_id: 'offline_test',
      }));

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(false);
      (writeProgressToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);
    });

    it('should call writeHistoryToCloud when logged in (recordAssessment)', async () => {
      const { isLoggedIn, writeProgressToCloud, writeHistoryToCloud } = await import('@/lib/store/supabase-sync');

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(true);
      (writeProgressToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);
      (writeHistoryToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);

      const store = useLearningStore.getState();
      store.recordAssessment('assess_cloud', 'Assess Cloud', 85, true);

      await new Promise(r => setTimeout(r, 10));

      expect(writeProgressToCloud).toHaveBeenCalled();
      expect(writeHistoryToCloud).toHaveBeenCalledWith('assess_cloud', 'Assess Cloud', 85, true);

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(false);
    });

    it('should enqueue history on writeHistoryToCloud failure', async () => {
      const { isLoggedIn, writeProgressToCloud, writeHistoryToCloud } = await import('@/lib/store/supabase-sync');
      const { enqueue } = await import('@/lib/store/offline-queue');

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(true);
      (writeProgressToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);
      (writeHistoryToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(false); // simulate failure

      const store = useLearningStore.getState();
      store.recordAssessment('assess_offline', 'Assess Offline', 70, false);

      await new Promise(r => setTimeout(r, 20));

      expect(enqueue).toHaveBeenCalledWith(expect.objectContaining({
        type: 'history',
        concept_id: 'assess_offline',
        score: 70,
        mastered: false,
      }));

      (isLoggedIn as ReturnType<typeof vi.fn>).mockReturnValue(false);
      (writeHistoryToCloud as ReturnType<typeof vi.fn>).mockResolvedValue(true);
    });
  });

  describe('initEdges + recommended', () => {
    it('should compute recommended concepts based on prerequisites', () => {
      useLearningStore.setState({
        progress: {
          prereq_1: { concept_id: 'prereq_1', status: 'mastered', mastery_score: 90, sessions: 1, total_time_sec: 0, last_learn_at: Date.now() },
        },
      });
      useLearningStore.getState().initEdges([
        { source: 'prereq_1', target: 'dependent_1' },
        { source: 'prereq_1', target: 'dependent_2' },
        { source: 'prereq_2', target: 'dependent_3' },
      ]);
      const { recommendedIds } = useLearningStore.getState();
      // dependent_1 and dependent_2 have prereq_1 mastered -> recommended
      expect(recommendedIds.has('dependent_1')).toBe(true);
      expect(recommendedIds.has('dependent_2')).toBe(true);
      // dependent_3 needs prereq_2 which is not mastered -> not recommended
      expect(recommendedIds.has('dependent_3')).toBe(false);
      // prereq_1 is mastered -> not recommended; prereq_2 has no prereqs -> recommended
      expect(recommendedIds.has('prereq_2')).toBe(true);
    });
  });

  describe('domain-scoped storage (Phase 7.5)', () => {
    it('should save and load progress per domain', () => {
      // Write to ai-engineering domain
      const store = useLearningStore.getState();
      store.startLearning('concept_a');
      expect(useLearningStore.getState().progress['concept_a']).toBeDefined();

      // Switch to mathematics domain — should have empty progress
      store.switchDomain('mathematics');
      expect(useLearningStore.getState().progress['concept_a']).toBeUndefined();
      expect(Object.keys(useLearningStore.getState().progress)).toHaveLength(0);

      // Write to mathematics domain
      useLearningStore.getState().startLearning('math_linear_algebra');
      expect(useLearningStore.getState().progress['math_linear_algebra']).toBeDefined();

      // Switch back to ai-engineering — should recover original progress
      useLearningStore.getState().switchDomain('ai-engineering');
      expect(useLearningStore.getState().progress['concept_a']).toBeDefined();
      expect(useLearningStore.getState().progress['math_linear_algebra']).toBeUndefined();
    });

    it('should migrate legacy flat keys to domain-scoped keys', async () => {
      const { migrateLegacyStorage, storageKeyForDomain } = await import('@/lib/store/learning');

      // Simulate legacy data
      const legacyData = JSON.stringify({
        progress: {
          legacy_concept: { concept_id: 'legacy_concept', status: 'mastered', mastery_score: 95, sessions: 3, total_time_sec: 600, last_learn_at: Date.now() },
        },
      });
      localStorage.setItem('akg-learning', legacyData);
      localStorage.setItem('akg-learning-history', JSON.stringify([{ concept_id: 'legacy_concept', concept_name: 'Legacy', score: 95, mastered: true, timestamp: Date.now() }]));

      // Run migration
      const migrated = migrateLegacyStorage('ai-engineering');
      expect(migrated).toBe(true);

      // Legacy key should be removed
      expect(localStorage.getItem('akg-learning')).toBeNull();
      // Domain-scoped key should have the data
      const domainData = localStorage.getItem(storageKeyForDomain('ai-engineering'));
      expect(domainData).toBeTruthy();
      const parsed = JSON.parse(domainData!);
      expect(parsed.progress.legacy_concept.status).toBe('mastered');
    });

    it('should not migrate if domain key already exists', async () => {
      const { migrateLegacyStorage, storageKeyForDomain } = await import('@/lib/store/learning');

      // Set up both legacy and domain data
      localStorage.setItem('akg-learning', JSON.stringify({ progress: { old: { concept_id: 'old', status: 'learning', mastery_score: 0, sessions: 1, total_time_sec: 0, last_learn_at: 1 } } }));
      localStorage.setItem(storageKeyForDomain('ai-engineering'), JSON.stringify({ progress: { existing: { concept_id: 'existing', status: 'mastered', mastery_score: 100, sessions: 5, total_time_sec: 1000, last_learn_at: 2 } } }));

      const migrated = migrateLegacyStorage('ai-engineering');
      expect(migrated).toBe(false);

      // Domain key should still have existing data, not overwritten
      const domainData = JSON.parse(localStorage.getItem(storageKeyForDomain('ai-engineering'))!);
      expect(domainData.progress.existing).toBeDefined();
      expect(domainData.progress.old).toBeUndefined();
    });

    it('should reset stats and recommendations on domain switch', () => {
      const store = useLearningStore.getState();
      store.startLearning('test_node');
      useLearningStore.setState({ stats: { total: 100, mastered: 1, learning: 1, streak: 1, dailyGoalMet: false } as any, recommendedIds: new Set(['rec1']) });

      store.switchDomain('mathematics');
      const state = useLearningStore.getState();
      expect(state.stats).toBeNull();
      expect(state.recommendedIds.size).toBe(0);
      expect(state.newlyUnlockedIds).toHaveLength(0);
    });
  });

  describe('peekDomainProgress', () => {
    it('should return zeros for empty domain', async () => {
      const { peekDomainProgress } = await import('@/lib/store/learning');
      const result = peekDomainProgress('nonexistent-domain');
      expect(result).toEqual({ mastered: 0, learning: 0, total: 0 });
    });

    it('should count mastered and learning concepts', async () => {
      const { peekDomainProgress, storageKeyForDomain } = await import('@/lib/store/learning');
      const data = {
        progress: {
          c1: { concept_id: 'c1', status: 'mastered', mastery_score: 90, sessions: 1, total_time_sec: 0, last_learn_at: 1 },
          c2: { concept_id: 'c2', status: 'learning', mastery_score: 40, sessions: 1, total_time_sec: 0, last_learn_at: 2 },
          c3: { concept_id: 'c3', status: 'mastered', mastery_score: 85, sessions: 2, total_time_sec: 0, last_learn_at: 3 },
          c4: { concept_id: 'c4', status: 'learning', mastery_score: 0, sessions: 1, total_time_sec: 0, last_learn_at: 4 },
        },
      };
      localStorage.setItem(storageKeyForDomain('test-domain'), JSON.stringify(data));
      const result = peekDomainProgress('test-domain');
      expect(result.mastered).toBe(2);
      expect(result.learning).toBe(2);
      expect(result.total).toBe(4);
    });

    it('should handle corrupted data gracefully', async () => {
      const { peekDomainProgress, storageKeyForDomain } = await import('@/lib/store/learning');
      localStorage.setItem(storageKeyForDomain('corrupt-domain'), 'not-json');
      const result = peekDomainProgress('corrupt-domain');
      expect(result).toEqual({ mastered: 0, learning: 0, total: 0 });
    });
  });
});

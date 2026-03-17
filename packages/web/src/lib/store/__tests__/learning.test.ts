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

// Mock supabase-sync (fire-and-forget, should not affect logic)
vi.mock('@/lib/store/supabase-sync', () => ({
  syncProgressToCloud: vi.fn(),
  syncHistoryToCloud: vi.fn(),
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
});

import { create } from 'zustand';
import type { LearningStats, UserConceptStatus } from '@akg/shared';

interface LearningState {
  stats: LearningStats | null;
  conceptStatuses: Map<string, UserConceptStatus>;

  setStats: (stats: LearningStats) => void;
  updateConceptStatus: (conceptId: string, status: UserConceptStatus) => void;
  setConceptStatuses: (statuses: UserConceptStatus[]) => void;
}

export const useLearningStore = create<LearningState>((set) => ({
  stats: null,
  conceptStatuses: new Map(),

  setStats: (stats) => set({ stats }),
  updateConceptStatus: (conceptId, status) =>
    set((state) => {
      const next = new Map(state.conceptStatuses);
      next.set(conceptId, status);
      return { conceptStatuses: next };
    }),
  setConceptStatuses: (statuses) =>
    set({
      conceptStatuses: new Map(statuses.map((s) => [s.concept_id, s])),
    }),
}));

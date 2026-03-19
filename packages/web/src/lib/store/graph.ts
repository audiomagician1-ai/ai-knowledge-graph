import { create } from 'zustand';
import type { GraphData, GraphNode } from '@akg/shared';
import { fetchGraphData as apiFetchGraphData } from '@/lib/api/graph-api';

interface GraphState {
  graphData: GraphData | null;
  selectedNode: GraphNode | null;
  activeSubdomain: string | null;
  loading: boolean;
  error: string | null;

  /** Load graph data from API for the given domain (or default) */
  loadGraphData: (domain?: string) => Promise<void>;
  setGraphData: (data: GraphData) => void;
  selectNode: (node: GraphNode | null) => void;
  setActiveSubdomain: (id: string | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  graphData: null,
  selectedNode: null,
  activeSubdomain: null,
  loading: false,
  error: null,

  loadGraphData: async (domain?: string) => {
    set({ loading: true, error: null, selectedNode: null, activeSubdomain: null });
    try {
      const data = await apiFetchGraphData(domain);
      set({ graphData: data, loading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : '加载图谱失败', loading: false });
    }
  },
  setGraphData: (data) => set({ graphData: data, loading: false }),
  selectNode: (node) => set({ selectedNode: node }),
  setActiveSubdomain: (id) => set({ activeSubdomain: id }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
}));

import { create } from 'zustand';
import type { GraphData, GraphNode } from '@akg/shared';

interface GraphState {
  graphData: GraphData | null;
  selectedNode: GraphNode | null;
  activeSubdomain: string | null;
  loading: boolean;
  error: string | null;

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

  setGraphData: (data) => set({ graphData: data, loading: false }),
  selectNode: (node) => set({ selectedNode: node }),
  setActiveSubdomain: (id) => set({ activeSubdomain: id }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
}));

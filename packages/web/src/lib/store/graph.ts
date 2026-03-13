import { create } from 'zustand';
import type { GraphData, GraphNode } from '@akg/shared';

interface GraphState {
  graphData: GraphData | null;
  selectedNode: GraphNode | null;
  loading: boolean;
  error: string | null;

  setGraphData: (data: GraphData) => void;
  selectNode: (node: GraphNode | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useGraphStore = create<GraphState>((set) => ({
  graphData: null,
  selectedNode: null,
  loading: false,
  error: null,

  setGraphData: (data) => set({ graphData: data, loading: false }),
  selectNode: (node) => set({ selectedNode: node }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error, loading: false }),
}));

/**
 * graph.ts store tests — graph state management
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useGraphStore } from '@/lib/store/graph';
import type { GraphData, GraphNode } from '@akg/shared';

// Mock the graph-api module
vi.mock('@/lib/api/graph-api', () => ({
  fetchGraphData: vi.fn(),
}));

import { fetchGraphData as mockFetchGraphData } from '@/lib/api/graph-api';

const mockNode: GraphNode = {
  id: 'test-node',
  label: '测试节点',
  domain_id: 'ai',
  subdomain_id: 'ml',
  difficulty: 3,
  status: 'not_started',
  is_milestone: false,
};

const mockGraphData: GraphData = {
  nodes: [mockNode],
  edges: [{ id: 'e1', source: 'a', target: 'b', relation_type: 'prerequisite', strength: 1.0 }],
};

describe('useGraphStore', () => {
  beforeEach(() => {
    useGraphStore.setState({
      graphData: null,
      selectedNode: null,
      activeSubdomain: null,
      loading: false,
      error: null,
    });
  });

  describe('initial state', () => {
    it('should have null graphData, selectedNode, activeSubdomain, error', () => {
      const state = useGraphStore.getState();
      expect(state.graphData).toBeNull();
      expect(state.selectedNode).toBeNull();
      expect(state.activeSubdomain).toBeNull();
      expect(state.error).toBeNull();
    });

    it('should have loading=false initially', () => {
      expect(useGraphStore.getState().loading).toBe(false);
    });
  });

  describe('setGraphData', () => {
    it('should set graphData and clear loading', () => {
      useGraphStore.setState({ loading: true });
      useGraphStore.getState().setGraphData(mockGraphData);
      const state = useGraphStore.getState();
      expect(state.graphData).toEqual(mockGraphData);
      expect(state.loading).toBe(false);
    });
  });

  describe('selectNode', () => {
    it('should set selectedNode', () => {
      useGraphStore.getState().selectNode(mockNode);
      expect(useGraphStore.getState().selectedNode).toEqual(mockNode);
    });

    it('should clear selectedNode with null', () => {
      useGraphStore.getState().selectNode(mockNode);
      useGraphStore.getState().selectNode(null);
      expect(useGraphStore.getState().selectedNode).toBeNull();
    });
  });

  describe('setActiveSubdomain', () => {
    it('should set activeSubdomain', () => {
      useGraphStore.getState().setActiveSubdomain('ml');
      expect(useGraphStore.getState().activeSubdomain).toBe('ml');
    });

    it('should clear activeSubdomain with null', () => {
      useGraphStore.getState().setActiveSubdomain('ml');
      useGraphStore.getState().setActiveSubdomain(null);
      expect(useGraphStore.getState().activeSubdomain).toBeNull();
    });
  });

  describe('setLoading', () => {
    it('should toggle loading state', () => {
      useGraphStore.getState().setLoading(true);
      expect(useGraphStore.getState().loading).toBe(true);
      useGraphStore.getState().setLoading(false);
      expect(useGraphStore.getState().loading).toBe(false);
    });
  });

  describe('setError', () => {
    it('should set error and clear loading', () => {
      useGraphStore.setState({ loading: true });
      useGraphStore.getState().setError('Network error');
      const state = useGraphStore.getState();
      expect(state.error).toBe('Network error');
      expect(state.loading).toBe(false);
    });

    it('should clear error with null', () => {
      useGraphStore.getState().setError('Some error');
      useGraphStore.getState().setError(null);
      expect(useGraphStore.getState().error).toBeNull();
    });
  });

  describe('loadGraphData', () => {
    beforeEach(() => {
      vi.clearAllMocks();
    });

    it('should fetch and set graph data for a domain', async () => {
      vi.mocked(mockFetchGraphData).mockResolvedValue(mockGraphData);

      await useGraphStore.getState().loadGraphData('ai-engineering');

      expect(mockFetchGraphData).toHaveBeenCalledWith('ai-engineering');
      const state = useGraphStore.getState();
      expect(state.graphData).toEqual(mockGraphData);
      expect(state.loading).toBe(false);
      expect(state.error).toBeNull();
    });

    it('should call API without domain when not specified', async () => {
      vi.mocked(mockFetchGraphData).mockResolvedValue(mockGraphData);

      await useGraphStore.getState().loadGraphData();

      expect(mockFetchGraphData).toHaveBeenCalledWith(undefined);
    });

    it('should reset selectedNode and activeSubdomain when loading', async () => {
      useGraphStore.setState({ selectedNode: mockNode, activeSubdomain: 'ml' });
      vi.mocked(mockFetchGraphData).mockResolvedValue(mockGraphData);

      await useGraphStore.getState().loadGraphData('ai-engineering');

      expect(useGraphStore.getState().selectedNode).toBeNull();
      expect(useGraphStore.getState().activeSubdomain).toBeNull();
    });

    it('should handle fetch error', async () => {
      vi.mocked(mockFetchGraphData).mockRejectedValue(new Error('Server down'));

      await useGraphStore.getState().loadGraphData('ai-engineering');

      const state = useGraphStore.getState();
      expect(state.graphData).toBeNull();
      expect(state.loading).toBe(false);
      expect(state.error).toBe('Server down');
    });

    it('should set loading=true during fetch', async () => {
      let resolvePromise: (v: GraphData) => void;
      vi.mocked(mockFetchGraphData).mockImplementation(
        () => new Promise<GraphData>((resolve) => { resolvePromise = resolve; })
      );

      const fetchPromise = useGraphStore.getState().loadGraphData('ai-engineering');
      expect(useGraphStore.getState().loading).toBe(true);

      resolvePromise!(mockGraphData);
      await fetchPromise;
      expect(useGraphStore.getState().loading).toBe(false);
    });
  });
});

import { useEffect, useCallback } from 'react';
import { useGraphStore } from '@/lib/store/graph';
import type { GraphNode } from '@akg/shared';

/**
 * Keyboard navigation for the graph page.
 * - Arrow keys (←→↑↓) to navigate between connected nodes
 * - Enter to start learning the selected node
 * - Escape to deselect
 *
 * @param onNodeSelect - callback when a node is navigated to
 * @param onLearnNode - callback when Enter is pressed on selected node
 */
export function useGraphKeyNav(
  onNodeSelect?: (node: GraphNode) => void,
  onLearnNode?: (node: GraphNode) => void,
) {
  const graphData = useGraphStore((s) => s.graphData);
  const selectedNode = useGraphStore((s) => s.selectedNode);
  const selectNode = useGraphStore((s) => s.selectNode);

  const findNeighbors = useCallback(
    (nodeId: string): GraphNode[] => {
      if (!graphData) return [];
      const neighborIds = new Set<string>();
      for (const edge of graphData.edges) {
        if (edge.source === nodeId) neighborIds.add(edge.target);
        if (edge.target === nodeId) neighborIds.add(edge.source);
      }
      return graphData.nodes.filter((n) => neighborIds.has(n.id));
    },
    [graphData],
  );

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Skip if typing in an input
      const tag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;

      if (!selectedNode || !graphData) return;

      // Enter → start learning
      if (e.key === 'Enter') {
        e.preventDefault();
        onLearnNode?.(selectedNode);
        return;
      }

      // Escape → deselect
      if (e.key === 'Escape') {
        e.preventDefault();
        selectNode(null);
        return;
      }

      // Arrow keys → navigate to connected nodes
      if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return;
      e.preventDefault();

      const neighbors = findNeighbors(selectedNode.id);
      if (neighbors.length === 0) return;

      // Sort neighbors by spatial logic:
      // ArrowUp/ArrowLeft → lower difficulty (prerequisites)
      // ArrowDown/ArrowRight → higher difficulty (dependents)
      const sorted = [...neighbors].sort((a, b) => a.difficulty - b.difficulty);

      let next: GraphNode | null = null;
      if (e.key === 'ArrowUp' || e.key === 'ArrowLeft') {
        // Go to a neighbor with lower or equal difficulty
        next = sorted.find((n) => n.difficulty <= selectedNode.difficulty && n.id !== selectedNode.id)
          || sorted[0];
      } else {
        // Go to a neighbor with higher or equal difficulty
        next = [...sorted].reverse().find((n) => n.difficulty >= selectedNode.difficulty && n.id !== selectedNode.id)
          || sorted[sorted.length - 1];
      }

      if (next && next.id !== selectedNode.id) {
        selectNode(next);
        onNodeSelect?.(next);
      }
    },
    [selectedNode, graphData, findNeighbors, selectNode, onNodeSelect, onLearnNode],
  );

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}
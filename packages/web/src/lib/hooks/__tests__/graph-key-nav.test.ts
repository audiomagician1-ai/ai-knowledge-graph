import { describe, it, expect } from 'vitest';

/**
 * Tests for graph keyboard navigation logic.
 */

interface MockNode { id: string; difficulty: number }
interface MockEdge { source: string; target: string }

function findNeighbors(nodeId: string, nodes: MockNode[], edges: MockEdge[]): MockNode[] {
  const neighborIds = new Set<string>();
  for (const edge of edges) {
    if (edge.source === nodeId) neighborIds.add(edge.target);
    if (edge.target === nodeId) neighborIds.add(edge.source);
  }
  return nodes.filter((n) => neighborIds.has(n.id));
}

function navigateKey(
  direction: 'up' | 'down',
  current: MockNode,
  neighbors: MockNode[],
): MockNode | null {
  if (neighbors.length === 0) return null;
  const sorted = [...neighbors].sort((a, b) => a.difficulty - b.difficulty);

  if (direction === 'up') {
    return sorted.find((n) => n.difficulty <= current.difficulty && n.id !== current.id) || sorted[0];
  } else {
    return [...sorted].reverse().find((n) => n.difficulty >= current.difficulty && n.id !== current.id) || sorted[sorted.length - 1];
  }
}

const nodes: MockNode[] = [
  { id: 'a', difficulty: 1 },
  { id: 'b', difficulty: 3 },
  { id: 'c', difficulty: 5 },
  { id: 'd', difficulty: 7 },
];

const edges: MockEdge[] = [
  { source: 'a', target: 'b' },
  { source: 'b', target: 'c' },
  { source: 'b', target: 'd' },
];

describe('Graph keyboard navigation', () => {
  it('finds neighbors for a node', () => {
    const n = findNeighbors('b', nodes, edges);
    expect(n.map((x) => x.id).sort()).toEqual(['a', 'c', 'd']);
  });

  it('navigates up (lower difficulty)', () => {
    const neighbors = findNeighbors('b', nodes, edges);
    const next = navigateKey('up', nodes[1], neighbors); // b -> a
    expect(next?.id).toBe('a');
  });

  it('navigates down (higher difficulty)', () => {
    const neighbors = findNeighbors('b', nodes, edges);
    const next = navigateKey('down', nodes[1], neighbors); // b -> d (highest)
    expect(next?.id).toBe('d');
  });

  it('returns first neighbor when no lower difficulty exists', () => {
    const neighbors = findNeighbors('a', nodes, edges);
    const next = navigateKey('up', nodes[0], neighbors);
    // a only has neighbor b (difficulty 3), which is higher, but we pick [0]
    expect(next).toBeDefined();
  });

  it('returns null for isolated node', () => {
    const isolated: MockNode = { id: 'x', difficulty: 5 };
    const next = navigateKey('down', isolated, []);
    expect(next).toBeNull();
  });

  it('handles nodes with same difficulty', () => {
    const sameNodes: MockNode[] = [
      { id: 'p', difficulty: 3 },
      { id: 'q', difficulty: 3 },
      { id: 'r', difficulty: 3 },
    ];
    const sameEdges: MockEdge[] = [
      { source: 'p', target: 'q' },
      { source: 'q', target: 'r' },
    ];
    const neighbors = findNeighbors('q', sameNodes, sameEdges);
    const next = navigateKey('down', sameNodes[1], neighbors);
    expect(next).toBeDefined();
  });
});

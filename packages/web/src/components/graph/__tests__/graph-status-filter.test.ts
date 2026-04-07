/**
 * Tests for GraphStatusFilter logic.
 */
import { describe, it, expect } from 'vitest';

type StatusFilterValue = 'all' | 'mastered' | 'learning' | 'not_started';

interface MockNode { id: string; status: string }

function countsByStatus(nodes: MockNode[]) {
  const mastered = nodes.filter(n => n.status === 'mastered').length;
  const learning = nodes.filter(n => n.status === 'learning').length;
  const notStarted = nodes.length - mastered - learning;
  return { mastered, learning, notStarted, total: nodes.length };
}

function filterNodes(nodes: MockNode[], filter: StatusFilterValue): MockNode[] {
  if (filter === 'all') return nodes;
  if (filter === 'not_started') return nodes.filter(n => n.status !== 'mastered' && n.status !== 'learning');
  return nodes.filter(n => n.status === filter);
}

describe('GraphStatusFilter logic', () => {
  const nodes: MockNode[] = [
    { id: 'a', status: 'mastered' },
    { id: 'b', status: 'mastered' },
    { id: 'c', status: 'learning' },
    { id: 'd', status: 'not_started' },
    { id: 'e', status: 'not_started' },
    { id: 'f', status: 'not_started' },
  ];

  it('counts status groups correctly', () => {
    const counts = countsByStatus(nodes);
    expect(counts.mastered).toBe(2);
    expect(counts.learning).toBe(1);
    expect(counts.notStarted).toBe(3);
    expect(counts.total).toBe(6);
  });

  it('filter all returns all nodes', () => {
    expect(filterNodes(nodes, 'all')).toHaveLength(6);
  });

  it('filter mastered returns only mastered', () => {
    const result = filterNodes(nodes, 'mastered');
    expect(result).toHaveLength(2);
    expect(result.every(n => n.status === 'mastered')).toBe(true);
  });

  it('filter learning returns only learning', () => {
    const result = filterNodes(nodes, 'learning');
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe('c');
  });

  it('filter not_started returns non-mastered non-learning', () => {
    const result = filterNodes(nodes, 'not_started');
    expect(result).toHaveLength(3);
    expect(result.every(n => n.status === 'not_started')).toBe(true);
  });

  it('handles empty nodes', () => {
    expect(countsByStatus([]).total).toBe(0);
    expect(filterNodes([], 'mastered')).toHaveLength(0);
  });
});

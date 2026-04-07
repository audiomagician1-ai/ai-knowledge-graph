/**
 * Tests for SubdomainFilter stats computation logic.
 */
import { describe, it, expect } from 'vitest';

interface MockNode { id: string; subdomain_id: string; status: string }

function computeSubdomainStats(nodes: MockNode[]) {
  const map = new Map<string, { total: number; mastered: number }>();
  for (const n of nodes) {
    const sub = n.subdomain_id || 'other';
    const entry = map.get(sub) || { total: 0, mastered: 0 };
    entry.total++;
    if (n.status === 'mastered') entry.mastered++;
    map.set(sub, entry);
  }
  return Array.from(map.entries())
    .map(([id, stats]) => ({ id, ...stats, pct: Math.round((stats.mastered / stats.total) * 100) }))
    .sort((a, b) => a.id.localeCompare(b.id));
}

describe('SubdomainFilter stats', () => {
  it('groups nodes by subdomain', () => {
    const nodes: MockNode[] = [
      { id: 'a', subdomain_id: 'basics', status: 'mastered' },
      { id: 'b', subdomain_id: 'basics', status: 'learning' },
      { id: 'c', subdomain_id: 'advanced', status: 'not_started' },
    ];
    const stats = computeSubdomainStats(nodes);
    expect(stats).toHaveLength(2);
    expect(stats[0].id).toBe('advanced');
    expect(stats[0].total).toBe(1);
    expect(stats[1].id).toBe('basics');
    expect(stats[1].total).toBe(2);
    expect(stats[1].mastered).toBe(1);
  });

  it('handles empty nodes', () => {
    expect(computeSubdomainStats([])).toHaveLength(0);
  });

  it('calculates mastery percentage per subdomain', () => {
    const nodes: MockNode[] = [
      { id: 'a', subdomain_id: 'sub-a', status: 'mastered' },
      { id: 'b', subdomain_id: 'sub-a', status: 'mastered' },
      { id: 'c', subdomain_id: 'sub-a', status: 'learning' },
      { id: 'd', subdomain_id: 'sub-a', status: 'not_started' },
    ];
    const stats = computeSubdomainStats(nodes);
    expect(stats[0].pct).toBe(50); // 2/4 = 50%
  });

  it('falls back to "other" for missing subdomain_id', () => {
    const nodes: MockNode[] = [
      { id: 'a', subdomain_id: '', status: 'mastered' },
      { id: 'b', subdomain_id: '', status: 'learning' },
    ];
    const stats = computeSubdomainStats(nodes);
    expect(stats[0].id).toBe('other');
    expect(stats[0].total).toBe(2);
  });

  it('sorts alphabetically', () => {
    const nodes: MockNode[] = [
      { id: 'a', subdomain_id: 'zebra', status: 'mastered' },
      { id: 'b', subdomain_id: 'alpha', status: 'learning' },
      { id: 'c', subdomain_id: 'middle', status: 'not_started' },
    ];
    const stats = computeSubdomainStats(nodes);
    expect(stats.map(s => s.id)).toEqual(['alpha', 'middle', 'zebra']);
  });
});

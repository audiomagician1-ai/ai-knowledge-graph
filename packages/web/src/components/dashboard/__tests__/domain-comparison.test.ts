/**
 * Tests for DomainComparison component logic.
 */
import { describe, it, expect } from 'vitest';

interface DomainStat {
  id: string;
  name: string;
  total: number;
  mastered: number;
  pct: number;
  color: string;
}

function computeDomainStats(
  domains: { id: string; name: string; total: number; color: string }[],
  maxDomains: number
): DomainStat[] {
  return domains
    .map(d => ({
      id: d.id,
      name: d.name,
      total: d.total,
      mastered: 0,
      pct: 0,
      color: d.color,
    }))
    .sort((a, b) => b.total - a.total || a.name.localeCompare(b.name))
    .slice(0, maxDomains);
}

describe('DomainComparison logic', () => {
  const sampleDomains = [
    { id: 'ai', name: 'AI编程', total: 400, color: '#8b5cf6' },
    { id: 'math', name: '数学', total: 269, color: '#3b82f6' },
    { id: 'eng', name: '英语', total: 200, color: '#f59e0b' },
    { id: 'physics', name: '物理', total: 194, color: '#22c55e' },
  ];

  it('sorts by total concepts descending', () => {
    const stats = computeDomainStats(sampleDomains, 10);
    expect(stats[0].id).toBe('ai');
    expect(stats[1].id).toBe('math');
    expect(stats[3].id).toBe('physics');
  });

  it('limits to maxDomains', () => {
    const stats = computeDomainStats(sampleDomains, 2);
    expect(stats).toHaveLength(2);
    expect(stats[0].id).toBe('ai');
    expect(stats[1].id).toBe('math');
  });

  it('handles empty domains', () => {
    expect(computeDomainStats([], 10)).toHaveLength(0);
  });

  it('preserves color from domain data', () => {
    const stats = computeDomainStats(sampleDomains, 10);
    expect(stats[0].color).toBe('#8b5cf6');
    expect(stats[2].color).toBe('#f59e0b');
  });

  it('percentage is 0 when no mastered concepts', () => {
    const stats = computeDomainStats(sampleDomains, 10);
    for (const s of stats) {
      expect(s.pct).toBe(0);
    }
  });
});

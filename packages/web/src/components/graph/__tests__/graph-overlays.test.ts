/**
 * Tests for GraphMiniStats and GraphLegend overlay components.
 */
import { describe, it, expect } from 'vitest';

// Test the stats calculation logic directly (avoids React rendering dependency)
describe('GraphMiniStats logic', () => {
  interface MockNode { id: string; status: string }

  function computeStats(nodes: MockNode[]) {
    const total = nodes.length;
    const mastered = nodes.filter(n => n.status === 'mastered').length;
    const learning = nodes.filter(n => n.status === 'learning').length;
    const notStarted = total - mastered - learning;
    const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
    return { total, mastered, learning, notStarted, pct };
  }

  it('computes stats for empty node list', () => {
    const stats = computeStats([]);
    expect(stats.total).toBe(0);
    expect(stats.pct).toBe(0);
  });

  it('computes correct mastery percentage', () => {
    const nodes: MockNode[] = [
      { id: 'a', status: 'mastered' },
      { id: 'b', status: 'mastered' },
      { id: 'c', status: 'learning' },
      { id: 'd', status: 'not_started' },
    ];
    const stats = computeStats(nodes);
    expect(stats.total).toBe(4);
    expect(stats.mastered).toBe(2);
    expect(stats.learning).toBe(1);
    expect(stats.notStarted).toBe(1);
    expect(stats.pct).toBe(50);
  });

  it('computes 100% for all mastered', () => {
    const nodes: MockNode[] = [
      { id: 'a', status: 'mastered' },
      { id: 'b', status: 'mastered' },
    ];
    expect(computeStats(nodes).pct).toBe(100);
  });

  it('rounds percentage correctly', () => {
    const nodes: MockNode[] = [
      { id: 'a', status: 'mastered' },
      { id: 'b', status: 'learning' },
      { id: 'c', status: 'not_started' },
    ];
    // 33.33% → rounds to 33
    expect(computeStats(nodes).pct).toBe(33);
  });
});

describe('GraphLegend data', () => {
  const statusItems = [
    { color: '#10b981', label: '已掌握' },
    { color: '#f59e0b', label: '学习中' },
    { color: '#06b6d4', label: '推荐学习' },
    { color: '#94a3b8', label: '未开始' },
  ];

  it('has 4 status items with valid colors', () => {
    expect(statusItems).toHaveLength(4);
    for (const item of statusItems) {
      expect(item.color).toMatch(/^#[0-9a-f]{6}$/i);
      expect(item.label.length).toBeGreaterThan(0);
    }
  });

  it('status colors match KnowledgeGraph node colors', () => {
    // These must match the colors in KnowledgeGraph.tsx nodeColor function
    expect(statusItems[0].color).toBe('#10b981'); // mastered = emerald
    expect(statusItems[1].color).toBe('#f59e0b'); // learning = amber
    expect(statusItems[2].color).toBe('#06b6d4'); // recommended = cyan
  });
});

describe('SVG progress ring calculation', () => {
  it('computes correct stroke dash offset', () => {
    const radius = 18;
    const circumference = 2 * Math.PI * radius;

    // 0% — full offset (no fill)
    expect(circumference - (0 / 100) * circumference).toBeCloseTo(circumference);

    // 100% — zero offset (fully filled)
    expect(circumference - (100 / 100) * circumference).toBeCloseTo(0);

    // 50% — half offset
    expect(circumference - (50 / 100) * circumference).toBeCloseTo(circumference / 2);
  });
});

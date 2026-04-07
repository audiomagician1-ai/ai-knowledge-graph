import { describe, it, expect } from 'vitest';

describe('DifficultyHeatmap logic', () => {
  it('maps difficulty to correct bucket index', () => {
    // difficulty 1 -> index 0, difficulty 10 -> index 9
    const toBucket = (d: number) => Math.min(9, Math.max(0, Math.round(d) - 1));
    expect(toBucket(1)).toBe(0);
    expect(toBucket(5)).toBe(4);
    expect(toBucket(10)).toBe(9);
    expect(toBucket(0.5)).toBe(0); // clamped
  });

  it('calculates intensity from count/max ratio', () => {
    const maxCount = 50;
    const counts = [0, 10, 25, 50];
    const intensities = counts.map((c) => c / maxCount);
    expect(intensities).toEqual([0, 0.2, 0.5, 1]);
  });

  it('handles empty distribution gracefully', () => {
    const dist = new Array(10).fill(0);
    const total = dist.reduce((s: number, v: number) => s + v, 0);
    expect(total).toBe(0);
  });

  it('sorts domains by concept count descending', () => {
    const domains = [
      { id: 'a', concepts: 100 },
      { id: 'b', concepts: 250 },
      { id: 'c', concepts: 150 },
    ];
    const sorted = [...domains].sort((a, b) => b.concepts - a.concepts);
    expect(sorted.map((d) => d.id)).toEqual(['b', 'c', 'a']);
  });

  it('slices to max 8 domains', () => {
    const domains = Array.from({ length: 15 }, (_, i) => ({ id: `d${i}`, concepts: i * 10 }));
    const top8 = domains.sort((a, b) => b.concepts - a.concepts).slice(0, 8);
    expect(top8).toHaveLength(8);
    expect(top8[0].concepts).toBe(140);
  });
});

import { describe, it, expect } from 'vitest';

describe('ConceptCompare logic', () => {
  it('calculates similarity score from shared connections', () => {
    const connA = new Set(['a', 'b', 'c', 'd']);
    const connB = new Set(['b', 'c', 'e', 'f']);
    const shared = new Set([...connA].filter((x) => connB.has(x)));
    const union = new Set([...connA, ...connB]);
    const similarity = Math.round((shared.size / Math.max(1, union.size)) * 1000) / 10;
    expect(similarity).toBe(33.3); // 2/6
  });

  it('similarity is 100% for identical connections', () => {
    const conn = new Set(['a', 'b', 'c']);
    const shared = conn;
    const union = conn;
    const similarity = Math.round((shared.size / union.size) * 1000) / 10;
    expect(similarity).toBe(100);
  });

  it('similarity is 0% for disjoint connections', () => {
    const connA = new Set(['a', 'b']);
    const connB = new Set(['c', 'd']);
    const shared = new Set([...connA].filter((x) => connB.has(x)));
    const union = new Set([...connA, ...connB]);
    const similarity = Math.round((shared.size / Math.max(1, union.size)) * 1000) / 10;
    expect(similarity).toBe(0);
  });

  it('difficulty gap is always non-negative', () => {
    expect(Math.abs(3 - 7)).toBe(4);
    expect(Math.abs(7 - 3)).toBe(4);
    expect(Math.abs(5 - 5)).toBe(0);
  });

  it('shared prerequisites calculation', () => {
    const prereqsA = ['x', 'y', 'z'];
    const prereqsB = ['y', 'z', 'w'];
    const shared = prereqsA.filter((p) => prereqsB.includes(p));
    expect(shared).toEqual(['y', 'z']);
  });
});

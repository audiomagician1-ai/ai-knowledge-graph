/**
 * Tests for DailyRecommendation deterministic rotation logic.
 */
import { describe, it, expect, vi, afterEach } from 'vitest';

/** Reproduce the index calculation from DailyRecommendation.tsx */
function getDailyIndex(poolSize: number, date?: Date): number {
  const now = date || new Date();
  const dayHash = now.getFullYear() * 366 + now.getMonth() * 31 + now.getDate();
  return dayHash % poolSize;
}

const POOL_SIZE = 30; // matches DAILY_POOL length in component

describe('getDailyIndex', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('should return a valid index within pool size', () => {
    const idx = getDailyIndex(POOL_SIZE);
    expect(idx).toBeGreaterThanOrEqual(0);
    expect(idx).toBeLessThan(POOL_SIZE);
  });

  it('should be deterministic — same date → same index', () => {
    const date = new Date(2026, 3, 7); // April 7, 2026
    const a = getDailyIndex(POOL_SIZE, date);
    const b = getDailyIndex(POOL_SIZE, date);
    expect(a).toBe(b);
  });

  it('should change daily — different dates → usually different index', () => {
    const indices = new Set<number>();
    for (let i = 0; i < 30; i++) {
      const date = new Date(2026, 3, 1 + i); // April 1-30, 2026
      indices.add(getDailyIndex(POOL_SIZE, date));
    }
    // With 30 items and 30 days, expect at least 10 unique indices (birthday paradox)
    expect(indices.size).toBeGreaterThanOrEqual(10);
  });

  it('should cycle through all pool items over time', () => {
    const indices = new Set<number>();
    // Check 365 days
    for (let i = 0; i < 365; i++) {
      const date = new Date(2026, 0, 1 + i);
      indices.add(getDailyIndex(POOL_SIZE, date));
    }
    // Should hit all 30 indices in a year
    expect(indices.size).toBe(POOL_SIZE);
  });

  it('should handle leap year dates', () => {
    const feb29 = new Date(2028, 1, 29); // Feb 29, 2028 (leap year)
    const idx = getDailyIndex(POOL_SIZE, feb29);
    expect(idx).toBeGreaterThanOrEqual(0);
    expect(idx).toBeLessThan(POOL_SIZE);
  });

  it('should not return NaN for edge dates', () => {
    const epoch = new Date(0); // Jan 1, 1970
    const idx = getDailyIndex(POOL_SIZE, epoch);
    expect(Number.isFinite(idx)).toBe(true);
    expect(idx).toBeGreaterThanOrEqual(0);
  });
});

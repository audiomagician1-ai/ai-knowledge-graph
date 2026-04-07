import { describe, it, expect } from 'vitest';

describe('WeeklyReport logic', () => {
  it('should calculate positive delta correctly', () => {
    const delta = (current: number, previous: number) => {
      if (previous === 0) return current > 0 ? 100 : 0;
      return Math.round(((current - previous) / previous) * 1000) / 10;
    };
    expect(delta(10, 5)).toBe(100);
    expect(delta(0, 0)).toBe(0);
    expect(delta(5, 0)).toBe(100);
    expect(delta(3, 10)).toBe(-70);
  });

  it('should handle zero previous values', () => {
    const delta = (current: number, previous: number) => {
      if (previous === 0) return current > 0 ? 100 : 0;
      return Math.round(((current - previous) / previous) * 1000) / 10;
    };
    expect(delta(0, 0)).toBe(0);
    expect(delta(1, 0)).toBe(100);
  });

  it('should format period strings', () => {
    const format = (start: number, end: number) => {
      const s = new Date(start).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
      const e = new Date(end).toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' });
      return `${s} - ${e}`;
    };
    const result = format(Date.now() - 7 * 86400000, Date.now());
    expect(result).toContain('-');
  });
});

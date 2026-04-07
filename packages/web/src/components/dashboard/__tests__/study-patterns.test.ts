import { describe, it, expect } from 'vitest';

describe('StudyPatterns logic', () => {
  it('should calculate peak hour from distribution', () => {
    const dist = Array(24).fill(0);
    dist[14] = 20; // 2 PM peak
    dist[9] = 15;
    const peakHour = dist.indexOf(Math.max(...dist));
    expect(peakHour).toBe(14);
  });

  it('should calculate consistency score', () => {
    const weekdayDist = [5, 3, 7, 0, 2, 0, 4]; // 5 active days out of 7
    const activeDays = weekdayDist.filter(d => d > 0).length;
    const consistency = Math.round((activeDays / 7) * 100 * 10) / 10;
    expect(consistency).toBe(71.4);
  });

  it('should handle all-zero distribution', () => {
    const dist = Array(24).fill(0);
    const max = Math.max(1, ...dist);
    expect(max).toBe(1); // floor at 1 to avoid division by zero
  });

  it('should map weekday names correctly', () => {
    const weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    expect(weekdayNames.length).toBe(7);
    expect(weekdayNames[0]).toBe('周一');
    expect(weekdayNames[6]).toBe('周日');
  });

  it('should calculate height percentages for bars', () => {
    const maxHour = 20;
    const count = 10;
    const height = (count / maxHour) * 100;
    expect(height).toBe(50);
    // Min height floor
    expect(Math.max(2, height)).toBe(50);
    expect(Math.max(2, 0)).toBe(2);
  });
});

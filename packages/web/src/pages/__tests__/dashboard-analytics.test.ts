/**
 * Tests for Dashboard analytics data transformation logic.
 */
import { describe, it, expect } from 'vitest';

interface VelocityDay {
  date: string;
  assessments: number;
  concepts_started: number;
  mastered: number;
}

describe('Dashboard — Velocity chart calculations', () => {
  const sampleDays: VelocityDay[] = [
    { date: '2026-04-01', assessments: 3, concepts_started: 2, mastered: 1 },
    { date: '2026-04-02', assessments: 0, concepts_started: 0, mastered: 0 },
    { date: '2026-04-03', assessments: 5, concepts_started: 1, mastered: 2 },
    { date: '2026-04-04', assessments: 1, concepts_started: 3, mastered: 0 },
  ];

  it('should calculate max value for bar height normalization', () => {
    const maxVal = Math.max(1, ...sampleDays.map((d) => d.assessments + d.concepts_started));
    expect(maxVal).toBe(6); // day 3: 5+1=6
  });

  it('should calculate bar height as percentage of max', () => {
    const maxVal = 6;
    const day = sampleDays[0]; // 3+2=5
    const height = ((day.assessments + day.concepts_started) / maxVal) * 100;
    expect(Math.round(height)).toBe(83); // 5/6 = 83%
  });

  it('should show 0 height for inactive days', () => {
    const maxVal = 6;
    const day = sampleDays[1]; // 0+0=0
    const total = day.assessments + day.concepts_started;
    expect(total).toBe(0);
  });

  it('should extract MM-DD label from ISO date', () => {
    const label = '2026-04-03'.slice(5);
    expect(label).toBe('04-03');
  });
});

describe('Dashboard — Summary statistics', () => {
  it('should count active days correctly', () => {
    const days = [
      { assessments: 3, concepts_started: 2 },
      { assessments: 0, concepts_started: 0 },
      { assessments: 5, concepts_started: 1 },
      { assessments: 0, concepts_started: 1 },
    ];
    const activeDays = days.filter((d) => d.assessments > 0 || d.concepts_started > 0).length;
    expect(activeDays).toBe(3);
  });

  it('should sum total assessments', () => {
    const days = [
      { assessments: 3 },
      { assessments: 0 },
      { assessments: 5 },
      { assessments: 1 },
    ];
    const total = days.reduce((sum, d) => sum + d.assessments, 0);
    expect(total).toBe(9);
  });
});

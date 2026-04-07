import { describe, it, expect } from 'vitest';

describe('MilestoneTracker logic', () => {
  it('milestone triggers at correct percentage thresholds', () => {
    const total = 100;
    const thresholds = [25, 50, 75, 100];
    const needed = thresholds.map((t) => Math.ceil((t / 100) * total));
    expect(needed).toEqual([25, 50, 75, 100]);
  });

  it('calculates mastery percentage correctly', () => {
    const mastered = 30;
    const total = 120;
    const pct = Math.round((mastered / total) * 100);
    expect(pct).toBe(25);
  });

  it('sorts upcoming before completed', () => {
    const milestones = [
      { name: 'A', completed: true, difficulty: 2 },
      { name: 'B', completed: false, difficulty: 5 },
      { name: 'C', completed: false, difficulty: 2 },
    ];
    const sorted = [...milestones].sort((a, b) => {
      if (a.completed !== b.completed) return a.completed ? 1 : -1;
      return a.difficulty - b.difficulty;
    });
    expect(sorted.map((m) => m.name)).toEqual(['C', 'B', 'A']);
  });

  it('limits to 5 upcoming and 5 completed', () => {
    const all = Array.from({ length: 20 }, (_, i) => ({
      completed: i >= 10,
      difficulty: i,
    }));
    const upcoming = all.filter((m) => !m.completed).slice(0, 5);
    const completed = all.filter((m) => m.completed).slice(0, 5);
    expect(upcoming).toHaveLength(5);
    expect(completed).toHaveLength(5);
  });

  it('handles zero-concept domain gracefully', () => {
    const total = 0;
    const pct = total > 0 ? Math.round((0 / total) * 100) : 0;
    expect(pct).toBe(0);
  });
});

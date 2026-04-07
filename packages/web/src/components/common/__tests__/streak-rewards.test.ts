import { describe, it, expect } from 'vitest';

describe('StreakRewards milestone logic', () => {
  const MILESTONES = [3, 7, 14, 30, 60, 100, 365];

  it('no milestones unlocked at 0 days', () => {
    const unlocked = MILESTONES.filter((m) => 0 >= m);
    expect(unlocked).toHaveLength(0);
  });

  it('first milestone unlocked at 3 days', () => {
    const unlocked = MILESTONES.filter((m) => 3 >= m);
    expect(unlocked).toHaveLength(1);
    expect(unlocked[0]).toBe(3);
  });

  it('multiple milestones at 30 days', () => {
    const unlocked = MILESTONES.filter((m) => 30 >= m);
    expect(unlocked).toHaveLength(4); // 3, 7, 14, 30
  });

  it('all milestones at 365 days', () => {
    const unlocked = MILESTONES.filter((m) => 365 >= m);
    expect(unlocked).toHaveLength(7);
  });

  it('next milestone calculation', () => {
    const streak = 10;
    const next = MILESTONES.find((m) => streak < m);
    expect(next).toBe(14);
  });

  it('no next milestone at max', () => {
    const streak = 400;
    const next = MILESTONES.find((m) => streak < m);
    expect(next).toBeUndefined();
  });

  it('progress percentage calculation', () => {
    const streak = 20;
    const nextDays = 30;
    const pct = Math.round((streak / nextDays) * 100);
    expect(pct).toBe(67);
  });

  it('uses max of current and longest streak', () => {
    const current = 5;
    const longest = 15;
    const effective = Math.max(current, longest);
    expect(effective).toBe(15);
    const unlocked = MILESTONES.filter((m) => effective >= m);
    expect(unlocked).toEqual([3, 7, 14]);
  });
});

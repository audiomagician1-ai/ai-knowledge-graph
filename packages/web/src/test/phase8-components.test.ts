import { describe, it, expect } from 'vitest';

describe('achievement-parts', () => {
  it('should export AchievementCard from AchievementParts.tsx', async () => {
    const mod = await import('@/components/panels/AchievementParts');
    expect(mod.AchievementCard).toBeDefined();
    expect(typeof mod.AchievementCard).toBe('function');
  });

  it('should export TIER_COLORS with 4 tiers', async () => {
    const mod = await import('@/components/panels/AchievementParts');
    expect(Object.keys(mod.TIER_COLORS)).toEqual(['bronze', 'silver', 'gold', 'platinum']);
  });

  it('should export TIER_LABELS with Chinese labels', async () => {
    const mod = await import('@/components/panels/AchievementParts');
    expect(mod.TIER_LABELS.gold).toBe('金');
    expect(mod.TIER_LABELS.platinum).toBe('铂金');
  });

  it('should export CATEGORY_META with 6 categories', async () => {
    const mod = await import('@/components/panels/AchievementParts');
    expect(Object.keys(mod.CATEGORY_META).length).toBe(6);
    expect(mod.CATEGORY_META.learning.label).toBe('学习里程碑');
  });
});

describe('study-goal-parts', () => {
  it('should export ProgressRing from StudyGoalParts.tsx', async () => {
    const mod = await import('@/components/common/StudyGoalParts');
    expect(mod.ProgressRing).toBeDefined();
    expect(typeof mod.ProgressRing).toBe('function');
  });

  it('should export GoalSettings from StudyGoalParts.tsx', async () => {
    const mod = await import('@/components/common/StudyGoalParts');
    expect(mod.GoalSettings).toBeDefined();
    expect(typeof mod.GoalSettings).toBe('function');
  });
});

describe('domain-card', () => {
  it('should export DomainCard from DomainCard.tsx', async () => {
    const mod = await import('@/components/panels/DomainCard');
    expect(mod.DomainCard).toBeDefined();
    expect(typeof mod.DomainCard).toBe('function');
  });
});

/**
 * V3.2 Frontend Component Tests — MasteryForecast, ReviewPriority, DifficultyAccuracy widgets
 */
import { describe, it, expect } from 'vitest';

describe('MasteryForecastWidget', () => {
  it('exports MasteryForecastWidget component', async () => {
    const mod = await import('../components/dashboard/MasteryForecastWidget');
    expect(mod.MasteryForecastWidget).toBeDefined();
    expect(typeof mod.MasteryForecastWidget).toBe('function');
  });
});

describe('ReviewPriorityWidget', () => {
  it('exports ReviewPriorityWidget component', async () => {
    const mod = await import('../components/dashboard/ReviewPriorityWidget');
    expect(mod.ReviewPriorityWidget).toBeDefined();
    expect(typeof mod.ReviewPriorityWidget).toBe('function');
  });
});

describe('DifficultyAccuracyWidget', () => {
  it('exports DifficultyAccuracyWidget component', async () => {
    const mod = await import('../components/dashboard/DifficultyAccuracyWidget');
    expect(mod.DifficultyAccuracyWidget).toBeDefined();
    expect(typeof mod.DifficultyAccuracyWidget).toBe('function');
  });
});

describe('DashboardPage V3.2 integration', () => {
  it('DashboardPage compiles with V3.2 lazy widgets', async () => {
    const mod = await import('../pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
    expect(typeof mod.DashboardPage).toBe('function');
  });
});
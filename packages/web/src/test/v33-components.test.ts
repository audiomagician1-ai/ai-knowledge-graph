/**
 * V3.3 Frontend Component Tests — DashboardWidgetGrid, NextMilestonesWidget
 */
import { describe, it, expect } from 'vitest';

describe('DashboardWidgetGrid', () => {
  it('exports DashboardWidgetGrid component', async () => {
    const mod = await import('../components/dashboard/DashboardWidgetGrid');
    expect(mod.DashboardWidgetGrid).toBeDefined();
    expect(typeof mod.DashboardWidgetGrid).toBe('function');
  });
});

describe('NextMilestonesWidget', () => {
  it('exports NextMilestonesWidget component', async () => {
    const mod = await import('../components/dashboard/NextMilestonesWidget');
    expect(mod.NextMilestonesWidget).toBeDefined();
    expect(typeof mod.NextMilestonesWidget).toBe('function');
  });
});

describe('DashboardPage V3.3', () => {
  it('DashboardPage compiles with DashboardWidgetGrid', async () => {
    const mod = await import('../pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
    expect(typeof mod.DashboardPage).toBe('function');
  });
});
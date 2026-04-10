/**
 * V3.5 Sprint FE Tests — SessionReplayWidget + ComparativeProgressWidget + DashboardWidgetGrid
 */
import { describe, it, expect } from 'vitest';

describe('V3.5 Dashboard Widgets', () => {
  it('SessionReplayWidget exports correctly', async () => {
    const mod = await import('../components/dashboard/SessionReplayWidget');
    expect(mod.SessionReplayWidget).toBeDefined();
    expect(typeof mod.SessionReplayWidget).toBe('function');
  });

  it('ComparativeProgressWidget exports correctly', async () => {
    const mod = await import('../components/dashboard/ComparativeProgressWidget');
    expect(mod.ComparativeProgressWidget).toBeDefined();
    expect(typeof mod.ComparativeProgressWidget).toBe('function');
  });

  it('DashboardWidgetGrid includes V3.5 new widgets', async () => {
    // V4.6: lazy imports moved to widget-registry.ts; grid references via W_.xxx
    const grid = await import('../components/dashboard/DashboardWidgetGrid?raw');
    expect(grid.default).toContain('SessionReplayWidget');
    expect(grid.default).toContain('ComparativeProgressWidget');
    const reg = await import('../components/dashboard/widget-registry?raw');
    const lazyCount = (reg.default.match(/lazy\(/g) || []).length;
    expect(lazyCount).toBeGreaterThanOrEqual(30);
  });

  it('SessionReplayWidget has proper interfaces', async () => {
    // Verify the module can be imported without errors
    const mod = await import('../components/dashboard/SessionReplayWidget');
    // Component should accept limit prop
    expect(mod.SessionReplayWidget.length).toBeLessThanOrEqual(1);
  });

  it('ComparativeProgressWidget has no required props', async () => {
    const mod = await import('../components/dashboard/ComparativeProgressWidget');
    // No required props
    expect(mod.ComparativeProgressWidget.length).toBe(0);
  });
});

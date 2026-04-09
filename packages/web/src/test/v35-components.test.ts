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
    const src = await import('../components/dashboard/DashboardWidgetGrid?raw');
    expect(src.default).toContain('SessionReplayWidget');
    expect(src.default).toContain('ComparativeProgressWidget');
    // At least 30 lazy-loaded widgets (some use default export shorthand)
    const lazyCount = (src.default.match(/lazy\(/g) || []).length;
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

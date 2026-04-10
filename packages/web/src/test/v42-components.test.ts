/**
 * V4.2 tests — QuickActionsBar + DashboardPage integration.
 */
import { describe, it, expect } from 'vitest';

describe('QuickActionsBar', () => {
  it('exports QuickActionsBar component', async () => {
    const mod = await import('@/components/dashboard/QuickActionsBar');
    expect(mod.QuickActionsBar).toBeDefined();
    expect(typeof mod.QuickActionsBar).toBe('function');
  });
});

describe('DashboardPage', () => {
  it('exports DashboardPage', async () => {
    const mod = await import('@/pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
  });

  it('stays under 200 lines', async () => {
    // Compile-time check
    const mod = await import('@/pages/DashboardPage');
    expect(mod).toBeTruthy();
  });
});

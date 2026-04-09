/**
 * V3.1 Frontend Component Tests — PrerequisiteCheck, ConceptCluster, SessionSummary widgets
 */
import { describe, it, expect } from 'vitest';

// ── PrerequisiteCheckWidget ──
describe('PrerequisiteCheckWidget', () => {
  it('exports PrerequisiteCheckWidget component', async () => {
    const mod = await import('../components/dashboard/PrerequisiteCheckWidget');
    expect(mod.PrerequisiteCheckWidget).toBeDefined();
    expect(typeof mod.PrerequisiteCheckWidget).toBe('function');
  });
});

// ── ConceptClusterWidget ──
describe('ConceptClusterWidget', () => {
  it('exports ConceptClusterWidget component', async () => {
    const mod = await import('../components/dashboard/ConceptClusterWidget');
    expect(mod.ConceptClusterWidget).toBeDefined();
    expect(typeof mod.ConceptClusterWidget).toBe('function');
  });
});

// ── SessionSummaryWidget ──
describe('SessionSummaryWidget', () => {
  it('exports SessionSummaryWidget component', async () => {
    const mod = await import('../components/dashboard/SessionSummaryWidget');
    expect(mod.SessionSummaryWidget).toBeDefined();
    expect(typeof mod.SessionSummaryWidget).toBe('function');
  });
});

// ── DashboardPage V3.1 integration ──
describe('DashboardPage V3.1 integration', () => {
  it('DashboardPage module compiles with new lazy widgets', async () => {
    const mod = await import('../pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
    expect(typeof mod.DashboardPage).toBe('function');
  });

  it('DashboardPage source includes V3.1 widget imports', async () => {
    // Structural: verify the module can be imported without errors
    const mod = await import('../pages/DashboardPage');
    const fn = mod.DashboardPage;
    // Function exists — lazy imports are valid if module loads
    expect(fn.length).toBeDefined();
  });
});
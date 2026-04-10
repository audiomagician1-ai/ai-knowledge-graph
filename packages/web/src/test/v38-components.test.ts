/**
 * V3.8 FE tests — ConceptJourneyWidget + LearningHeatmapWidget + DashboardWidgetGrid update.
 */
import { describe, it, expect } from 'vitest';

describe('V3.8 FE: ConceptJourneyWidget', () => {
  it('exports named component', async () => {
    const mod = await import('../components/dashboard/ConceptJourneyWidget');
    expect(mod.ConceptJourneyWidget).toBeDefined();
    expect(typeof mod.ConceptJourneyWidget).toBe('function');
  });

  it('file is under 200 lines', async () => {
    // Component should be concise
    const mod = await import('../components/dashboard/ConceptJourneyWidget?raw');
    const lines = (mod.default as string).split('\n').length;
    expect(lines).toBeLessThan(200);
  });
});

describe('V3.8 FE: LearningHeatmapWidget', () => {
  it('exports named component', async () => {
    const mod = await import('../components/dashboard/LearningHeatmapWidget');
    expect(mod.LearningHeatmapWidget).toBeDefined();
    expect(typeof mod.LearningHeatmapWidget).toBe('function');
  });

  it('file is under 200 lines', async () => {
    const mod = await import('../components/dashboard/LearningHeatmapWidget?raw');
    const lines = (mod.default as string).split('\n').length;
    expect(lines).toBeLessThan(200);
  });
});

describe('V3.8 FE: DashboardWidgetGrid integration', () => {
  it('exports DashboardWidgetGrid', async () => {
    const mod = await import('../components/dashboard/DashboardWidgetGrid');
    expect(mod.DashboardWidgetGrid).toBeDefined();
  });

  it('widget grid source includes new V3.8 widgets', async () => {
    const mod = await import('../components/dashboard/DashboardWidgetGrid?raw');
    const src = mod.default as string;
    expect(src).toContain('ConceptJourneyWidget');
    expect(src).toContain('LearningHeatmapWidget');
  });

  it('widget grid file stays under 200 lines', async () => {
    const mod = await import('../components/dashboard/DashboardWidgetGrid?raw');
    const lines = (mod.default as string).split('\n').length;
    expect(lines).toBeLessThan(200);
  });
});

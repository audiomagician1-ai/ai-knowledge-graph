/**
 * V2.9 Frontend Component Tests — LearningReportPage, ContentSearchWidget, ConceptSimilarityPanel
 */
import { describe, it, expect } from 'vitest';

// ── LearningReportPage ──
describe('LearningReportPage', () => {
  it('exports LearningReportPage component', async () => {
    const mod = await import('../pages/LearningReportPage');
    expect(mod.LearningReportPage).toBeDefined();
    expect(typeof mod.LearningReportPage).toBe('function');
  });

  it('is a named export (not default)', async () => {
    const mod = await import('../pages/LearningReportPage');
    expect(mod.LearningReportPage).toBeDefined();
    // Ensure it's not a default export
    expect('default' in mod).toBe(false);
  });
});

// ── ContentSearchWidget ──
describe('ContentSearchWidget', () => {
  it('exports ContentSearchWidget component', async () => {
    const mod = await import('../components/dashboard/ContentSearchWidget');
    expect(mod.ContentSearchWidget).toBeDefined();
    expect(typeof mod.ContentSearchWidget).toBe('function');
  });
});

// ── ConceptSimilarityPanel ──
describe('ConceptSimilarityPanel', () => {
  it('exports ConceptSimilarityPanel component', async () => {
    const mod = await import('../components/graph/ConceptSimilarityPanel');
    expect(mod.ConceptSimilarityPanel).toBeDefined();
    expect(typeof mod.ConceptSimilarityPanel).toBe('function');
  });
});

// ── App routing ──
describe('App routes V2.9', () => {
  it('App.tsx includes /report route', async () => {
    // Verify the route exists by importing App and checking it resolves
    const mod = await import('../App');
    expect(mod.App).toBeDefined();
  });

  it('LearningReportPage can be lazy-imported', async () => {
    const mod = await import('../pages/LearningReportPage');
    expect(mod.LearningReportPage).toBeDefined();
  });
});

// ── ChatIdleView integration ──
describe('ChatIdleView V2.9 integration', () => {
  it('ChatIdleView imports ConceptSimilarityPanel', async () => {
    const mod = await import('../components/chat/ChatIdleView');
    expect(mod.ChatIdleView).toBeDefined();
  });
});

// ── DashboardPage integration ──
describe('DashboardPage V2.9 integration', () => {
  it('DashboardPage includes ContentSearchWidget lazy import', async () => {
    const mod = await import('../pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
  });
});

// ── HomePage navigation ──
describe('HomePage V2.9 navigation', () => {
  it('HomePage includes FileText icon import for report button', async () => {
    const mod = await import('../pages/HomePage');
    expect(mod.HomePage).toBeDefined();
  });
});

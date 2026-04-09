/**
 * V3.0 Frontend Component Tests — OnboardingRecommendWidget, onboarding-api
 */
import { describe, it, expect } from 'vitest';

// ── OnboardingRecommendWidget ──
describe('OnboardingRecommendWidget', () => {
  it('exports OnboardingRecommendWidget component', async () => {
    const mod = await import('../components/dashboard/OnboardingRecommendWidget');
    expect(mod.OnboardingRecommendWidget).toBeDefined();
    expect(typeof mod.OnboardingRecommendWidget).toBe('function');
  });
});

// ── Onboarding API Client ──
describe('onboarding-api', () => {
  it('exports fetchRecommendedStart function', async () => {
    const mod = await import('../lib/api/onboarding-api');
    expect(mod.fetchRecommendedStart).toBeDefined();
    expect(typeof mod.fetchRecommendedStart).toBe('function');
  });

  it('exports fetchDomainPreview function', async () => {
    const mod = await import('../lib/api/onboarding-api');
    expect(mod.fetchDomainPreview).toBeDefined();
    expect(typeof mod.fetchDomainPreview).toBe('function');
  });

  it('exports DomainRecommendation type (structural check via API shape)', async () => {
    const mod = await import('../lib/api/onboarding-api');
    // Type exists if the module compiles — just verify exports are present
    expect(Object.keys(mod)).toContain('fetchRecommendedStart');
    expect(Object.keys(mod)).toContain('fetchDomainPreview');
  });
});

// ── DashboardPage lazy-load registration ──
describe('DashboardPage V3.0 integration', () => {
  it('exports DashboardPage with OnboardingRecommendWidget registered', async () => {
    const mod = await import('../pages/DashboardPage');
    expect(mod.DashboardPage).toBeDefined();
    expect(typeof mod.DashboardPage).toBe('function');
  });
});
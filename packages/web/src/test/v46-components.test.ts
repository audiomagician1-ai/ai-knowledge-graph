/**
 * V4.6 Component Tests — Dashboard Scalability + API Explorer + Code Health
 */
import { describe, it, expect } from 'vitest';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

const dashDir = join(__dirname, '..', 'components', 'dashboard');
const pagesDir = join(__dirname, '..', 'pages');

describe('V4.6: DashboardWidgetGrid code health split', () => {
  it('DashboardWidgetGrid should be under 140L after registry extraction', () => {
    const content = readFileSync(join(dashDir, 'DashboardWidgetGrid.tsx'), 'utf-8');
    const lines = content.split('\n').length;
    expect(lines).toBeLessThan(140);
  });

  it('widget-registry.ts should exist and export all 45 widgets', () => {
    const path = join(dashDir, 'widget-registry.ts');
    expect(existsSync(path)).toBe(true);
    const content = readFileSync(path, 'utf-8');
    const exports = content.match(/export const /g);
    expect(exports).not.toBeNull();
    expect(exports!.length).toBeGreaterThanOrEqual(45);
  });

  it('DashboardWidgetGrid should import from widget-registry', () => {
    const content = readFileSync(join(dashDir, 'DashboardWidgetGrid.tsx'), 'utf-8');
    expect(content).toContain("from './widget-registry'");
    // Should NOT have local lazy() imports
    expect(content).not.toContain("const AdaptivePathWidget = lazy(");
  });
});

describe('V4.6: OnboardingRecommendWidget split', () => {
  it('OnboardingRecommendWidget should be under 100L after modal extraction', () => {
    const content = readFileSync(join(dashDir, 'OnboardingRecommendWidget.tsx'), 'utf-8');
    const lines = content.split('\n').length;
    expect(lines).toBeLessThan(100);
  });

  it('DomainPreviewModal should exist as separate file', () => {
    const path = join(dashDir, 'DomainPreviewModal.tsx');
    expect(existsSync(path)).toBe(true);
    const content = readFileSync(path, 'utf-8');
    expect(content).toContain('export function DomainPreviewModal');
    expect(content).toContain('DomainPreviewResponse');
  });

  it('OnboardingRecommendWidget should import DomainPreviewModal', () => {
    const content = readFileSync(join(dashDir, 'OnboardingRecommendWidget.tsx'), 'utf-8');
    expect(content).toContain("import { DomainPreviewModal }");
  });
});

describe('V4.6: API Explorer Page', () => {
  it('ApiExplorerPage should exist with proper exports', () => {
    const path = join(pagesDir, 'ApiExplorerPage.tsx');
    expect(existsSync(path)).toBe(true);
    const content = readFileSync(path, 'utf-8');
    expect(content).toContain('export function ApiExplorerPage');
    expect(content).toContain('/api/health/api-catalog');
  });

  it('ApiExplorerPage should be under 200 lines', () => {
    const content = readFileSync(join(pagesDir, 'ApiExplorerPage.tsx'), 'utf-8');
    const lines = content.split('\n').length;
    expect(lines).toBeLessThanOrEqual(200);
  });

  it('App.tsx should have /api-explorer route', () => {
    const content = readFileSync(join(__dirname, '..', 'App.tsx'), 'utf-8');
    expect(content).toContain('/api-explorer');
    expect(content).toContain('ApiExplorerPage');
  });

  it('ApiExplorerPage should have search and try-it functionality', () => {
    const content = readFileSync(join(pagesDir, 'ApiExplorerPage.tsx'), 'utf-8');
    expect(content).toContain('setSearch');
    expect(content).toContain('tryEndpoint');
    expect(content).toContain('tryResult');
  });
});

describe('V4.6: ApiHealthWidget links to explorer', () => {
  it('ApiHealthWidget should link to /api-explorer', () => {
    const content = readFileSync(join(dashDir, 'ApiHealthWidget.tsx'), 'utf-8');
    expect(content).toContain('/api-explorer');
    expect(content).toContain('useNavigate');
  });
});

describe('V4.6: All dashboard components under 200L', () => {
  it('no dashboard widget should exceed 200 lines', () => {
    const fs = require('fs');
    const files: string[] = fs.readdirSync(dashDir).filter((f: string) => f.endsWith('.tsx'));
    const violations: string[] = [];
    for (const f of files) {
      const lines = readFileSync(join(dashDir, f), 'utf-8').split('\n').length;
      if (lines > 200) violations.push(`${f}: ${lines}L`);
    }
    expect(violations).toEqual([]);
  });
});
/**
 * V4.3 Component Tests — DifficultyTunerWidget + PortfolioExportWidget + DashboardWidgetGrid updates
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const comp = (name: string) => resolve(__dirname, '..', 'components', 'dashboard', name);
const read = (name: string) => readFileSync(comp(name), 'utf-8');

describe('V4.3 DifficultyTunerWidget', () => {
  const src = read('DifficultyTunerWidget.tsx');

  it('exports DifficultyTunerWidget', () => {
    expect(src).toContain('export function DifficultyTunerWidget');
  });
  it('fetches difficulty-tuner API', () => {
    expect(src).toContain('/api/analytics/difficulty-tuner');
  });
  it('shows direction arrows (too_easy / too_hard)', () => {
    expect(src).toContain('too_easy');
    expect(src).toContain('too_hard');
  });
  it('displays confidence percentage', () => {
    expect(src).toContain('confidence');
    expect(src).toContain('Math.round');
  });
  it('navigates to concept on click', () => {
    expect(src).toContain('useNavigate');
    expect(src).toContain('nav(`/graph');
  });
  it('respects 200L component limit', () => {
    const lines = src.split('\n').length;
    expect(lines).toBeLessThanOrEqual(200);
  });
});

describe('V4.3 PortfolioExportWidget', () => {
  const src = read('PortfolioExportWidget.tsx');

  it('exports PortfolioExportWidget', () => {
    expect(src).toContain('export function PortfolioExportWidget');
  });
  it('fetches portfolio API and unwraps portfolio key', () => {
    expect(src).toContain('/api/learning/portfolio');
    expect(src).toContain('.portfolio');
  });
  it('exports Markdown format', () => {
    expect(src).toContain('toMarkdown');
    expect(src).toContain('learning-portfolio.md');
    expect(src).toContain('text/markdown');
  });
  it('exports JSON format', () => {
    expect(src).toContain('learning-portfolio.json');
    expect(src).toContain('application/json');
  });
  it('shows skills radar progress bars', () => {
    expect(src).toContain('mastery_pct');
    expect(src).toContain('bg-indigo-400');
  });
  it('shows strengths and growth areas', () => {
    expect(src).toContain('strengths');
    expect(src).toContain('growth_areas');
  });
  it('respects 200L component limit', () => {
    const lines = src.split('\n').length;
    expect(lines).toBeLessThanOrEqual(200);
  });
});

describe('V4.3 DashboardWidgetGrid integration', () => {
  const src = read('DashboardWidgetGrid.tsx');

  it('lazy-loads DifficultyTunerWidget', () => {
    expect(src).toContain("DifficultyTunerWidget");
    expect(src).toContain("import('./DifficultyTunerWidget')");
  });
  it('lazy-loads PortfolioExportWidget', () => {
    expect(src).toContain("PortfolioExportWidget");
    expect(src).toContain("import('./PortfolioExportWidget')");
  });
  it('has 41+ lazy imports (39 previous + 2 new)', () => {
    const lazyCount = (src.match(/lazy\(/g) || []).length;
    expect(lazyCount).toBeGreaterThanOrEqual(41);
  });
  it('stays under 200 lines', () => {
    const lines = src.split('\n').length;
    expect(lines).toBeLessThanOrEqual(200);
  });
});

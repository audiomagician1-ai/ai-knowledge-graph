/**
 * V4.4 Component Tests — LearningCalendarWidget + KnowledgeMapWidget + grid integration
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const comp = (name: string) => resolve(__dirname, '..', 'components', 'dashboard', name);
const read = (name: string) => readFileSync(comp(name), 'utf-8');

describe('V4.4 LearningCalendarWidget', () => {
  const src = read('LearningCalendarWidget.tsx');

  it('exports LearningCalendarWidget', () => {
    expect(src).toContain('export function LearningCalendarWidget');
  });
  it('fetches learning-calendar API', () => {
    expect(src).toContain('/api/analytics/learning-calendar');
  });
  it('renders intensity-based color grid', () => {
    expect(src).toContain('INTENSITY_COLORS');
    expect(src).toContain('bg-emerald');
  });
  it('shows future review overlay', () => {
    expect(src).toContain('FUTURE_BG');
    expect(src).toContain('reviews_due');
  });
  it('has hover tooltip', () => {
    expect(src).toContain('hoveredDay');
    expect(src).toContain('onMouseEnter');
  });
  it('has legend', () => {
    expect(src).toContain('待复习');
  });
  it('respects 200L limit', () => {
    expect(src.split('\n').length).toBeLessThanOrEqual(200);
  });
});

describe('V4.4 KnowledgeMapWidget', () => {
  const src = read('KnowledgeMapWidget.tsx');

  it('exports KnowledgeMapWidget', () => {
    expect(src).toContain('export function KnowledgeMapWidget');
  });
  it('fetches knowledge-map-stats API', () => {
    expect(src).toContain('/api/analytics/knowledge-map-stats');
  });
  it('shows coverage progress bar', () => {
    expect(src).toContain('coverage_pct');
    expect(src).toContain('bg-gradient-to-r');
  });
  it('shows exploration style', () => {
    expect(src).toContain('深度型');
    expect(src).toContain('广度型');
    expect(src).toContain('均衡型');
  });
  it('shows difficulty breakdown bars', () => {
    expect(src).toContain('difficulty_breakdown');
  });
  it('navigates to domain on click', () => {
    expect(src).toContain('useNavigate');
    expect(src).toContain('nav(`/graph');
  });
  it('respects 200L limit', () => {
    expect(src.split('\n').length).toBeLessThanOrEqual(200);
  });
});

describe('V4.4 DashboardWidgetGrid integration', () => {
  const gridSrc = read('DashboardWidgetGrid.tsx');
  const regSrc = read('widget-registry.ts');

  it('lazy-loads LearningCalendarWidget', () => {
    expect(gridSrc).toContain("LearningCalendarWidget");
    expect(regSrc).toContain("import('./LearningCalendarWidget')");
  });
  it('lazy-loads KnowledgeMapWidget', () => {
    expect(gridSrc).toContain("KnowledgeMapWidget");
    expect(regSrc).toContain("import('./KnowledgeMapWidget')");
  });
  it('has 43+ lazy imports', () => {
    const lazyCount = (regSrc.match(/lazy\(/g) || []).length;
    expect(lazyCount).toBeGreaterThanOrEqual(43);
  });
  it('stays under 200 lines', () => {
    expect(gridSrc.split('\n').length).toBeLessThanOrEqual(200);
  });
});

/**
 * V4.5 Component Tests — DailySummaryWidget + AchievementShowcaseWidget + grid integration
 */
import { describe, it, expect } from 'vitest';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const comp = (name: string) => resolve(__dirname, '..', 'components', 'dashboard', name);
const read = (name: string) => readFileSync(comp(name), 'utf-8');

describe('V4.5 DailySummaryWidget', () => {
  const src = read('DailySummaryWidget.tsx');

  it('exports DailySummaryWidget', () => {
    expect(src).toContain('export function DailySummaryWidget');
  });
  it('fetches daily-summary API', () => {
    expect(src).toContain('/api/analytics/daily-summary');
  });
  it('shows streak with fire icon', () => {
    expect(src).toContain('Flame');
    expect(src).toContain('streak');
  });
  it('shows recommended action button', () => {
    expect(src).toContain('recommended_action');
    expect(src).toContain('ArrowRight');
  });
  it('shows motivation message', () => {
    expect(src).toContain('motivation');
  });
  it('navigates on action click', () => {
    expect(src).toContain('useNavigate');
    expect(src).toContain('nav(ra.route)');
  });
  it('respects 200L limit', () => {
    expect(src.split('\n').length).toBeLessThanOrEqual(200);
  });
});

describe('V4.5 AchievementShowcaseWidget', () => {
  const src = read('AchievementShowcaseWidget.tsx');

  it('exports AchievementShowcaseWidget', () => {
    expect(src).toContain('export function AchievementShowcaseWidget');
  });
  it('fetches achievements API', () => {
    expect(src).toContain('/api/learning/achievements');
  });
  it('shows tier badges', () => {
    expect(src).toContain('TIER_COLORS');
    expect(src).toContain('bronze');
    expect(src).toContain('gold');
    expect(src).toContain('platinum');
  });
  it('shows category icons', () => {
    expect(src).toContain('CAT_ICONS');
    expect(src).toContain('learning');
    expect(src).toContain('streak');
  });
  it('shows progress bar', () => {
    expect(src).toContain('bg-yellow-400');
    expect(src).toContain('unlocked_count');
  });
  it('shows next to unlock', () => {
    expect(src).toContain('即将解锁');
    expect(src).toContain('Lock');
  });
  it('respects 200L limit', () => {
    expect(src.split('\n').length).toBeLessThanOrEqual(200);
  });
});

describe('V4.5 DashboardWidgetGrid integration', () => {
  const gridSrc = read('DashboardWidgetGrid.tsx');
  const regSrc = read('widget-registry.ts');

  it('lazy-loads DailySummaryWidget', () => {
    expect(gridSrc).toContain("DailySummaryWidget");
    expect(regSrc).toContain("import('./DailySummaryWidget')");
  });
  it('lazy-loads AchievementShowcaseWidget', () => {
    expect(gridSrc).toContain("AchievementShowcaseWidget");
    expect(regSrc).toContain("import('./AchievementShowcaseWidget')");
  });
  it('has 45+ lazy imports', () => {
    const lazyCount = (regSrc.match(/lazy\(/g) || []).length;
    expect(lazyCount).toBeGreaterThanOrEqual(45);
  });
  it('stays under 200 lines', () => {
    expect(gridSrc.split('\n').length).toBeLessThanOrEqual(200);
  });
});

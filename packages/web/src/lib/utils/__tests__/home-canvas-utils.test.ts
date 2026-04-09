import { describe, it, expect } from 'vitest';
import {
  DEMO_DOMAINS, NAME_MAP, completeness, buildRectHexGrid,
  BG, BASE_R, HEX_SPACING, FISH_MAX, FISH_MIN, FISH_POWER,
} from '../home-canvas-utils';

/**
 * Tests for home-canvas-utils.ts (V2.4 God File split from HomePage.tsx).
 * Validates static data + pure logic functions.
 */

describe('DEMO_DOMAINS', () => {
  it('has at least 30 domains', () => {
    expect(DEMO_DOMAINS.length).toBeGreaterThanOrEqual(30);
  });

  it('all domains have required fields', () => {
    for (const d of DEMO_DOMAINS) {
      expect(d.id).toBeTruthy();
      expect(d.name).toBeTruthy();
      expect(d.color).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(d.is_active).toBe(true);
      expect(d.stats?.total_concepts).toBeGreaterThan(0);
    }
  });

  it('has unique domain IDs', () => {
    const ids = DEMO_DOMAINS.map(d => d.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  it('ai-engineering is the first domain (center of hex grid)', () => {
    expect(DEMO_DOMAINS[0].id).toBe('ai-engineering');
  });
});

describe('NAME_MAP', () => {
  it('maps ai-engineering to AI编程', () => {
    expect(NAME_MAP['ai-engineering']).toBe('AI编程');
  });
});

describe('completeness()', () => {
  it('calculates weighted completeness score', () => {
    expect(completeness(100, 50, 10)).toBe(100 + 25 + 50); // 175
    expect(completeness(0, 0, 0)).toBe(0);
    expect(completeness(200, 100, 5)).toBe(200 + 50 + 25); // 275
  });
});

describe('buildRectHexGrid()', () => {
  it('returns enough positions for given count', () => {
    const grid = buildRectHexGrid(36, 114);
    expect(grid.totalSlots).toBeGreaterThanOrEqual(36);
    expect(grid.positions.length).toBe(grid.totalSlots);
  });

  it('positions are sorted by distance from center', () => {
    const grid = buildRectHexGrid(10, 100);
    for (let i = 1; i < grid.positions.length; i++) {
      const dPrev = grid.positions[i - 1].x ** 2 + grid.positions[i - 1].y ** 2;
      const dCurr = grid.positions[i].x ** 2 + grid.positions[i].y ** 2;
      expect(dCurr).toBeGreaterThanOrEqual(dPrev - 0.001); // float tolerance
    }
  });

  it('wrapW and wrapH are positive', () => {
    const grid = buildRectHexGrid(20, 80);
    expect(grid.wrapW).toBeGreaterThan(0);
    expect(grid.wrapH).toBeGreaterThan(0);
  });

  it('center position is near origin', () => {
    const grid = buildRectHexGrid(25, 100);
    const center = grid.positions[0];
    expect(Math.abs(center.x)).toBeLessThan(100);
    expect(Math.abs(center.y)).toBeLessThan(100);
  });
});

describe('Canvas constants', () => {
  it('BG is a valid light color', () => {
    expect(BG).toBe('#f0f0ec');
  });

  it('fisheye parameters are within valid ranges', () => {
    expect(FISH_MAX).toBeGreaterThan(1);
    expect(FISH_MIN).toBeGreaterThan(0);
    expect(FISH_MIN).toBeLessThan(1);
    expect(FISH_POWER).toBeGreaterThan(1);
  });

  it('BASE_R and HEX_SPACING are positive', () => {
    expect(BASE_R).toBeGreaterThan(0);
    expect(HEX_SPACING).toBeGreaterThan(BASE_R);
  });
});
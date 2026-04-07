import { describe, it, expect } from 'vitest';

describe('DomainRadar math', () => {
  const SIZE = 240;
  const CENTER = SIZE / 2;
  const RADIUS = 90;

  const getXY = (i: number, n: number, r: number): [number, number] => {
    const angleStep = (2 * Math.PI) / n;
    const angle = -Math.PI / 2 + i * angleStep;
    return [CENTER + r * Math.cos(angle), CENTER + r * Math.sin(angle)];
  };

  it('first point should be at top (12 o\'clock position)', () => {
    const [x, y] = getXY(0, 4, RADIUS);
    expect(Math.round(x)).toBe(CENTER); // centered horizontally
    expect(y).toBeLessThan(CENTER); // above center
  });

  it('all points should be within SVG bounds', () => {
    for (let n = 3; n <= 8; n++) {
      for (let i = 0; i < n; i++) {
        const [x, y] = getXY(i, n, RADIUS);
        expect(x).toBeGreaterThan(0);
        expect(x).toBeLessThan(SIZE);
        expect(y).toBeGreaterThan(0);
        expect(y).toBeLessThan(SIZE);
      }
    }
  });

  it('mastery percentage maps to correct radius', () => {
    const pct = 75;
    const r = (pct / 100) * RADIUS;
    expect(r).toBe(67.5);
  });

  it('0% mastery still gets minimum radius of 4px', () => {
    const pct = 0;
    const r = (pct / 100) * RADIUS;
    const clamped = Math.max(r, 4);
    expect(clamped).toBe(4);
  });

  it('polygon points form closed shape with correct count', () => {
    const n = 5;
    const pts = Array.from({ length: n }, (_, i) => getXY(i, n, 50));
    expect(pts).toHaveLength(n);
    // First and last should be different points (SVG polygon auto-closes)
    const [x0, y0] = pts[0];
    const [xn, yn] = pts[n - 1];
    expect(Math.abs(x0 - xn) + Math.abs(y0 - yn)).toBeGreaterThan(1);
  });

  it('text anchor logic: left=end, right=start, center=middle', () => {
    const getAnchor = (x: number) =>
      x < CENTER - 5 ? 'end' : x > CENTER + 5 ? 'start' : 'middle';
    expect(getAnchor(50)).toBe('end');
    expect(getAnchor(190)).toBe('start');
    expect(getAnchor(CENTER)).toBe('middle');
  });
});

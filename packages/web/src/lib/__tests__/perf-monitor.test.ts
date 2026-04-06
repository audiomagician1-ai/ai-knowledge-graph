/**
 * Performance monitor utility tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { getPerfMetrics, initPerfMonitor } from '../utils/perf-monitor';

describe('Performance Monitor', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('getPerfMetrics returns an object', () => {
    const metrics = getPerfMetrics();
    expect(typeof metrics).toBe('object');
    // Before init, most values should be undefined
    // After init, they may be populated depending on environment
  });

  it('initPerfMonitor does not throw in jsdom environment', () => {
    // jsdom has limited PerformanceObserver support
    expect(() => initPerfMonitor()).not.toThrow();
  });

  it('getPerfMetrics returns a copy, not the original object', () => {
    const a = getPerfMetrics();
    const b = getPerfMetrics();
    expect(a).not.toBe(b);
    expect(a).toEqual(b);
  });

  it('metrics values are numbers or undefined', () => {
    const m = getPerfMetrics();
    for (const [, v] of Object.entries(m)) {
      expect(v === undefined || typeof v === 'number').toBe(true);
    }
  });
});

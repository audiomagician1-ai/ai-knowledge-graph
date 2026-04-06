/**
 * Performance monitoring utilities — track Core Web Vitals and page load metrics.
 * Uses the native PerformanceObserver API (no external dependencies).
 * 
 * Usage: call `initPerfMonitor()` once at app boot to begin collecting metrics.
 * Metrics are logged to the console in development and can be sent to an analytics endpoint.
 */
import { createLogger } from './logger';

const log = createLogger('Perf');

export interface PerfMetrics {
  /** First Contentful Paint (ms) */
  fcp?: number;
  /** Largest Contentful Paint (ms) */
  lcp?: number;
  /** Time to First Byte (ms) */
  ttfb?: number;
  /** DOM Content Loaded (ms) */
  dcl?: number;
  /** Full page load (ms) */
  load?: number;
  /** Number of JS chunks loaded */
  jsChunks?: number;
  /** Total JS transfer size (bytes) */
  jsTransferSize?: number;
}

const metrics: PerfMetrics = {};

/** Get current collected metrics */
export function getPerfMetrics(): Readonly<PerfMetrics> {
  return { ...metrics };
}

/**
 * Initialize performance monitoring.
 * Call once in main.tsx after React root mount.
 */
export function initPerfMonitor(): void {
  if (typeof window === 'undefined' || !('PerformanceObserver' in window)) return;

  // ── Navigation Timing (TTFB, DCL, Load) ──
  try {
    const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined;
    if (nav) {
      metrics.ttfb = Math.round(nav.responseStart - nav.requestStart);
      metrics.dcl = Math.round(nav.domContentLoadedEventEnd - nav.startTime);
      metrics.load = Math.round(nav.loadEventEnd - nav.startTime);
    }
  } catch { /* Safari fallback */ }

  // ── FCP (First Contentful Paint) ──
  try {
    const fcpObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          metrics.fcp = Math.round(entry.startTime);
          log.info('FCP', { ms: metrics.fcp });
          fcpObserver.disconnect();
        }
      }
    });
    fcpObserver.observe({ type: 'paint', buffered: true });
  } catch { /* not supported */ }

  // ── LCP (Largest Contentful Paint) ──
  try {
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const last = entries[entries.length - 1];
      if (last) {
        metrics.lcp = Math.round(last.startTime);
      }
    });
    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });

    // Report LCP on page hide (final value)
    const reportLCP = () => {
      lcpObserver.disconnect();
      if (metrics.lcp) {
        log.info('LCP', { ms: metrics.lcp });
      }
    };
    document.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'hidden') reportLCP();
    }, { once: true });
  } catch { /* not supported */ }

  // ── JS Resource Stats ──
  try {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
    const jsResources = resources.filter(r => r.name.endsWith('.js'));
    metrics.jsChunks = jsResources.length;
    metrics.jsTransferSize = jsResources.reduce((sum, r) => sum + (r.transferSize || 0), 0);
    log.info('JS bundles', { chunks: metrics.jsChunks, transferKB: Math.round(metrics.jsTransferSize / 1024) });
  } catch { /* not supported */ }
}

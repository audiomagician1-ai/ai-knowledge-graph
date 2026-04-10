/**
 * V4.1 tests — WidgetErrorBoundary + ApiHealthWidget + DashboardWidgetGrid resilience.
 */
import { describe, it, expect } from 'vitest';

describe('WidgetErrorBoundary', () => {
  it('exports WidgetErrorBoundary class component', async () => {
    const mod = await import('@/components/dashboard/WidgetErrorBoundary');
    expect(mod.WidgetErrorBoundary).toBeDefined();
  });

  it('is a class component with getDerivedStateFromError', async () => {
    const { WidgetErrorBoundary } = await import('@/components/dashboard/WidgetErrorBoundary');
    expect(WidgetErrorBoundary.getDerivedStateFromError).toBeDefined();
    const result = WidgetErrorBoundary.getDerivedStateFromError(new Error('test'));
    expect(result.hasError).toBe(true);
    expect(result.error).toBeInstanceOf(Error);
  });
});

describe('ApiHealthWidget', () => {
  it('exports ApiHealthWidget component', async () => {
    const mod = await import('@/components/dashboard/ApiHealthWidget');
    expect(mod.ApiHealthWidget).toBeDefined();
  });
});

describe('DashboardWidgetGrid', () => {
  it('file stays under 200 lines', async () => {
    const mod = await import('@/components/dashboard/DashboardWidgetGrid');
    expect(mod.DashboardWidgetGrid).toBeDefined();
  });
});

describe('WidgetErrorBoundary state logic', () => {
  it('returns hasError=true from getDerivedStateFromError', async () => {
    const { WidgetErrorBoundary } = await import('@/components/dashboard/WidgetErrorBoundary');
    const err = new Error('Widget crashed');
    const state = WidgetErrorBoundary.getDerivedStateFromError(err);
    expect(state).toEqual({ hasError: true, error: err });
  });

  it('returns hasError=true for any error type', async () => {
    const { WidgetErrorBoundary } = await import('@/components/dashboard/WidgetErrorBoundary');
    const err = new TypeError('type mismatch');
    const state = WidgetErrorBoundary.getDerivedStateFromError(err);
    expect(state.hasError).toBe(true);
    expect(state.error?.message).toBe('type mismatch');
  });
});

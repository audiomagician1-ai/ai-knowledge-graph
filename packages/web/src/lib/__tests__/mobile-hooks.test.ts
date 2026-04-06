/**
 * Tests for mobile-oriented hooks (useBackButton, useKeyboardHeight, useAppLifecycle)
 */
import { describe, it, expect, vi, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useKeyboardHeight } from '../hooks/useKeyboardHeight';
import { useAppLifecycle } from '../hooks/useAppLifecycle';

describe('useKeyboardHeight', () => {
  it('returns 0 by default (web mode)', () => {
    const { result } = renderHook(() => useKeyboardHeight());
    expect(result.current).toBe(0);
  });
});

describe('useAppLifecycle', () => {
  afterEach(() => {
    // Restore visibility state
    Object.defineProperty(document, 'visibilityState', {
      writable: true,
      value: 'visible',
    });
  });

  it('calls onForeground when tab becomes visible', () => {
    const onForeground = vi.fn();
    renderHook(() => useAppLifecycle({ onForeground }));

    // Simulate going hidden then visible
    Object.defineProperty(document, 'visibilityState', {
      writable: true,
      value: 'hidden',
    });
    act(() => { document.dispatchEvent(new Event('visibilitychange')); });

    Object.defineProperty(document, 'visibilityState', {
      writable: true,
      value: 'visible',
    });
    act(() => { document.dispatchEvent(new Event('visibilitychange')); });

    expect(onForeground).toHaveBeenCalledTimes(1);
  });

  it('calls onBackground when tab becomes hidden', () => {
    const onBackground = vi.fn();
    renderHook(() => useAppLifecycle({ onBackground }));

    Object.defineProperty(document, 'visibilityState', {
      writable: true,
      value: 'hidden',
    });
    act(() => { document.dispatchEvent(new Event('visibilitychange')); });

    expect(onBackground).toHaveBeenCalledTimes(1);
  });

  it('cleans up on unmount', () => {
    const onForeground = vi.fn();
    const { unmount } = renderHook(() => useAppLifecycle({ onForeground }));
    unmount();

    // After unmount, events should not trigger callback
    Object.defineProperty(document, 'visibilityState', {
      writable: true,
      value: 'visible',
    });
    document.dispatchEvent(new Event('visibilitychange'));
    expect(onForeground).not.toHaveBeenCalled();
  });
});

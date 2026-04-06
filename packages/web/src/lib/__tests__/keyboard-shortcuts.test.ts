import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts';

function fireKey(key: string, opts: Partial<KeyboardEventInit> = {}) {
  document.dispatchEvent(new KeyboardEvent('keydown', { key, bubbles: true, ...opts }));
}

describe('useKeyboardShortcuts', () => {
  let handler: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    handler = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should call handler on matching key press', () => {
    renderHook(() => useKeyboardShortcuts([{ key: 'Escape', handler }]));
    fireKey('Escape');
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('should not call handler for non-matching key', () => {
    renderHook(() => useKeyboardShortcuts([{ key: 'Escape', handler }]));
    fireKey('Enter');
    expect(handler).not.toHaveBeenCalled();
  });

  it('should handle Ctrl+key shortcuts', () => {
    renderHook(() => useKeyboardShortcuts([{ key: 'k', ctrl: true, handler }]));
    fireKey('k', { ctrlKey: true });
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('should not trigger Ctrl shortcut without Ctrl pressed', () => {
    renderHook(() => useKeyboardShortcuts([{ key: 'k', ctrl: true, handler }]));
    fireKey('k');
    expect(handler).not.toHaveBeenCalled();
  });

  it('should handle Shift+key shortcuts', () => {
    renderHook(() => useKeyboardShortcuts([{ key: '?', shift: true, handler }]));
    fireKey('?', { shiftKey: true });
    expect(handler).toHaveBeenCalledTimes(1);
  });

  it('should handle multiple shortcuts', () => {
    const handler2 = vi.fn();
    renderHook(() => useKeyboardShortcuts([
      { key: 'Escape', handler },
      { key: 'Enter', handler: handler2 },
    ]));
    fireKey('Escape');
    fireKey('Enter');
    expect(handler).toHaveBeenCalledTimes(1);
    expect(handler2).toHaveBeenCalledTimes(1);
  });

  it('should clean up on unmount', () => {
    const { unmount } = renderHook(() => useKeyboardShortcuts([{ key: 'Escape', handler }]));
    unmount();
    fireKey('Escape');
    expect(handler).not.toHaveBeenCalled();
  });

  it('should handle Meta key (Mac Cmd)', () => {
    renderHook(() => useKeyboardShortcuts([{ key: 'k', ctrl: true, handler }]));
    fireKey('k', { metaKey: true });
    expect(handler).toHaveBeenCalledTimes(1);
  });
});

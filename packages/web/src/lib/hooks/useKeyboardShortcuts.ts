import { useEffect, useCallback } from 'react';

interface ShortcutDef {
  /** Key to listen for (e.g., 'Escape', 'k', '/') */
  key: string;
  /** Whether Ctrl/Cmd is required */
  ctrl?: boolean;
  /** Whether Shift is required */
  shift?: boolean;
  /** Callback when shortcut triggers */
  handler: () => void;
  /** Description for UI help tooltip */
  description?: string;
}

/**
 * Register keyboard shortcuts with proper modifier detection.
 * 
 * Features:
 * - Ignores shortcuts when user is typing in input/textarea/contenteditable
 * - Supports Ctrl (Windows) and Cmd (Mac) modifiers
 * - Cleanup on unmount
 * 
 * Usage:
 *   useKeyboardShortcuts([
 *     { key: 'Escape', handler: () => navigate('/') },
 *     { key: 'k', ctrl: true, handler: () => openSearch() },
 *   ]);
 */
export function useKeyboardShortcuts(shortcuts: ShortcutDef[]) {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Skip if user is typing in an input element
    const tag = (e.target as HTMLElement)?.tagName;
    const isEditable = (e.target as HTMLElement)?.isContentEditable;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || isEditable) return;

    for (const shortcut of shortcuts) {
      const ctrlMatch = shortcut.ctrl
        ? (e.ctrlKey || e.metaKey)
        : (!e.ctrlKey && !e.metaKey);
      const shiftMatch = shortcut.shift ? e.shiftKey : !e.shiftKey;

      if (e.key === shortcut.key && ctrlMatch && shiftMatch) {
        e.preventDefault();
        shortcut.handler();
        return;
      }
    }
  }, [shortcuts]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);
}

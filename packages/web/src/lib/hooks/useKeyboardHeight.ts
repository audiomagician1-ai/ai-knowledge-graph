/**
 * React hook for virtual keyboard height on mobile.
 * Returns the current keyboard height in pixels (0 when hidden).
 * Uses Capacitor Keyboard plugin on native, falls back to 0 on web.
 *
 * Usage:
 *   const keyboardHeight = useKeyboardHeight();
 *   <div style={{ paddingBottom: keyboardHeight }}>...</div>
 */
import { useState, useEffect } from 'react';
import { keyboard } from '@/lib/utils/capacitor';

export function useKeyboardHeight(): number {
  const [height, setHeight] = useState(0);

  useEffect(() => {
    const cleanup = keyboard.onVisibilityChange(
      (kbHeight) => setHeight(kbHeight),
      () => setHeight(0),
    );
    return cleanup;
  }, []);

  return height;
}

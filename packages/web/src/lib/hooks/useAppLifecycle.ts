/**
 * React hook for app lifecycle events (foreground/background).
 * Works on both web (visibilitychange) and native Capacitor (appStateChange).
 *
 * Usage:
 *   useAppLifecycle({
 *     onForeground: () => { refreshData(); },
 *     onBackground: () => { saveState(); },
 *   });
 */
import { useEffect } from 'react';
import { appLifecycle } from '@/lib/utils/capacitor';

interface AppLifecycleOptions {
  /** Called when app returns to foreground */
  onForeground?: () => void;
  /** Called when app goes to background */
  onBackground?: () => void;
}

export function useAppLifecycle({ onForeground, onBackground }: AppLifecycleOptions) {
  useEffect(() => {
    const cleanup = appLifecycle.onStateChange((isActive) => {
      if (isActive) {
        onForeground?.();
      } else {
        onBackground?.();
      }
    });
    return cleanup;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}

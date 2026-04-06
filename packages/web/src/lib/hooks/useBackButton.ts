/**
 * React hook for Android hardware back button handling.
 * Falls back to browser history.back() on web.
 *
 * Usage:
 *   useBackButton(() => {
 *     if (isModalOpen) { closeModal(); return; }
 *     navigate(-1);
 *   });
 */
import { useEffect } from 'react';
import { appLifecycle, platform } from '@/lib/utils/capacitor';

/**
 * Register a handler for the Android back button.
 * On web/iOS this is a no-op (browsers handle back natively).
 *
 * @param handler - Called when back button is pressed. Use to close modals or navigate.
 */
export function useBackButton(handler: () => void) {
  useEffect(() => {
    if (platform.platform !== 'android') return;
    return appLifecycle.onBackButton(handler);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}

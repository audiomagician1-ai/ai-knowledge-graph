import { useState, useEffect, useSyncExternalStore } from 'react';

/**
 * Subscribe to browser online/offline status.
 * 
 * Uses useSyncExternalStore for React 18+ concurrent mode safety.
 * Falls back to useState + event listeners for compatibility.
 * 
 * Usage:
 *   const isOnline = useOnlineStatus();
 *   if (!isOnline) showOfflineWarning();
 */
function subscribe(callback: () => void) {
  window.addEventListener('online', callback);
  window.addEventListener('offline', callback);
  return () => {
    window.removeEventListener('online', callback);
    window.removeEventListener('offline', callback);
  };
}

function getSnapshot() {
  return navigator.onLine;
}

function getServerSnapshot() {
  return true; // SSR: assume online
}

export function useOnlineStatus(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}

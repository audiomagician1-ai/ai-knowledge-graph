/**
 * Capacitor platform abstraction layer.
 * 
 * Provides unified APIs that work in both web browser and native Capacitor contexts.
 * All native APIs are lazy-imported so they don't crash in web-only environments.
 * 
 * Usage:
 *   import { platform, storage, keyboard } from '@/lib/utils/capacitor';
 *   if (platform.isNative) { ... }
 *   await storage.set('key', 'value');
 */
import { createLogger } from './logger';

const log = createLogger('Capacitor');

// ── Platform Detection ──────────────────────────────────────

interface PlatformInfo {
  /** True when running inside a native Capacitor shell (Android/iOS) */
  isNative: boolean;
  /** True when running in a web browser (not native) */
  isWeb: boolean;
  /** 'android' | 'ios' | 'web' */
  platform: 'android' | 'ios' | 'web';
}

function detectPlatform(): PlatformInfo {
  try {
    // Capacitor.isNativePlatform() is the official way
    const cap = (window as any).Capacitor;
    if (cap?.isNativePlatform?.()) {
      const p = cap.getPlatform?.() || 'web';
      return { isNative: true, isWeb: false, platform: p as 'android' | 'ios' };
    }
  } catch { /* not available */ }
  return { isNative: false, isWeb: true, platform: 'web' };
}

export const platform: PlatformInfo = detectPlatform();


// ── Storage (Preferences API fallback to localStorage) ──────

export const storage = {
  async get(key: string): Promise<string | null> {
    if (platform.isNative) {
      try {
        const { Preferences } = await import('@capacitor/preferences');
        const { value } = await Preferences.get({ key });
        return value;
      } catch (e) {
        log.warn('Preferences.get failed, falling back to localStorage', { key });
      }
    }
    return localStorage.getItem(key);
  },

  async set(key: string, value: string): Promise<void> {
    if (platform.isNative) {
      try {
        const { Preferences } = await import('@capacitor/preferences');
        await Preferences.set({ key, value });
        return;
      } catch (e) {
        log.warn('Preferences.set failed, falling back to localStorage', { key });
      }
    }
    localStorage.setItem(key, value);
  },

  async remove(key: string): Promise<void> {
    if (platform.isNative) {
      try {
        const { Preferences } = await import('@capacitor/preferences');
        await Preferences.remove({ key });
        return;
      } catch (e) {
        log.warn('Preferences.remove failed, falling back to localStorage', { key });
      }
    }
    localStorage.removeItem(key);
  },
};


// ── Keyboard Management ─────────────────────────────────────

export const keyboard = {
  /** Hide the virtual keyboard (no-op on web) */
  async hide(): Promise<void> {
    if (!platform.isNative) return;
    try {
      const { Keyboard } = await import('@capacitor/keyboard');
      await Keyboard.hide();
    } catch { /* plugin not available */ }
  },

  /** Register keyboard show/hide listeners. Returns cleanup function. */
  onVisibilityChange(
    onShow: (height: number) => void,
    onHide: () => void,
  ): () => void {
    if (!platform.isNative) return () => {};
    
    let showHandler: any;
    let hideHandler: any;

    import('@capacitor/keyboard').then(({ Keyboard }) => {
      showHandler = Keyboard.addListener('keyboardWillShow', (info) => {
        onShow(info.keyboardHeight);
      });
      hideHandler = Keyboard.addListener('keyboardWillHide', () => {
        onHide();
      });
    }).catch(() => { /* not available */ });

    return () => {
      showHandler?.remove?.();
      hideHandler?.remove?.();
    };
  },
};


// ── Status Bar ──────────────────────────────────────────────

export const statusBar = {
  /** Set status bar to dark content (light background) */
  async setDark(): Promise<void> {
    if (!platform.isNative) return;
    try {
      const { StatusBar, Style } = await import('@capacitor/status-bar');
      await StatusBar.setStyle({ style: Style.Dark });
      await StatusBar.setBackgroundColor({ color: '#0f172a' });
    } catch { /* not available */ }
  },
};


// ── App Lifecycle ───────────────────────────────────────────

export const appLifecycle = {
  /**
   * Register app state change listener.
   * Callback receives `true` when app comes to foreground, `false` when backgrounded.
   * Returns cleanup function.
   */
  onStateChange(callback: (isActive: boolean) => void): () => void {
    if (!platform.isNative) {
      // Web fallback: use visibilitychange
      const handler = () => callback(document.visibilityState === 'visible');
      document.addEventListener('visibilitychange', handler);
      return () => document.removeEventListener('visibilitychange', handler);
    }

    let handler: any;
    import('@capacitor/app').then(({ App }) => {
      handler = App.addListener('appStateChange', ({ isActive }) => {
        callback(isActive);
      });
    }).catch(() => { /* not available */ });

    return () => { handler?.remove?.(); };
  },

  /** Register back button handler (Android). Returns cleanup function. */
  onBackButton(callback: () => void): () => void {
    if (platform.platform !== 'android') return () => {};

    let handler: any;
    import('@capacitor/app').then(({ App }) => {
      handler = App.addListener('backButton', () => {
        callback();
      });
    }).catch(() => { /* not available */ });

    return () => { handler?.remove?.(); };
  },
};


// ── Initialization ──────────────────────────────────────────

/**
 * Initialize Capacitor plugins on app start.
 * Safe to call in web environments (all calls are no-ops).
 */
export async function initCapacitor(): Promise<void> {
  if (!platform.isNative) {
    log.info('Web mode — Capacitor plugins skipped');
    return;
  }

  log.info('Native mode detected', { platform: platform.platform });

  // Configure status bar
  await statusBar.setDark();

  // Hide splash screen after a brief delay
  try {
    const { SplashScreen } = await import('@capacitor/splash-screen');
    await SplashScreen.hide({ fadeOutDuration: 300 });
  } catch { /* not available */ }

  log.info('Capacitor initialized');
}

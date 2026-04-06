/**
 * Capacitor platform abstraction layer tests.
 * In test environment (jsdom), everything should run in web-fallback mode.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { platform, storage, keyboard, statusBar, appLifecycle, initCapacitor } from '../utils/capacitor';

describe('Capacitor Platform Detection', () => {
  it('detects web platform in test environment', () => {
    expect(platform.isWeb).toBe(true);
    expect(platform.isNative).toBe(false);
    expect(platform.platform).toBe('web');
  });
});

describe('Capacitor Storage (localStorage fallback)', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('set and get a value', async () => {
    await storage.set('test-key', 'test-value');
    const value = await storage.get('test-key');
    expect(value).toBe('test-value');
  });

  it('get returns null for missing key', async () => {
    const value = await storage.get('nonexistent');
    expect(value).toBeNull();
  });

  it('remove deletes a key', async () => {
    await storage.set('remove-test', 'data');
    await storage.remove('remove-test');
    const value = await storage.get('remove-test');
    expect(value).toBeNull();
  });
});

describe('Capacitor Keyboard (web no-op)', () => {
  it('hide() does not throw on web', async () => {
    await expect(keyboard.hide()).resolves.toBeUndefined();
  });

  it('onVisibilityChange returns cleanup function on web', () => {
    const cleanup = keyboard.onVisibilityChange(() => {}, () => {});
    expect(typeof cleanup).toBe('function');
    cleanup(); // should not throw
  });
});

describe('Capacitor StatusBar (web no-op)', () => {
  it('setDark() does not throw on web', async () => {
    await expect(statusBar.setDark()).resolves.toBeUndefined();
  });
});

describe('Capacitor App Lifecycle', () => {
  it('onStateChange returns cleanup function', () => {
    const callback = vi.fn();
    const cleanup = appLifecycle.onStateChange(callback);
    expect(typeof cleanup).toBe('function');
    cleanup();
  });

  it('onStateChange fires on visibilitychange in web mode', () => {
    const callback = vi.fn();
    const cleanup = appLifecycle.onStateChange(callback);
    
    // Simulate visibility change
    Object.defineProperty(document, 'visibilityState', {
      writable: true,
      value: 'hidden',
    });
    document.dispatchEvent(new Event('visibilitychange'));
    expect(callback).toHaveBeenCalledWith(false);
    
    Object.defineProperty(document, 'visibilityState', {
      writable: true,
      value: 'visible',
    });
    document.dispatchEvent(new Event('visibilitychange'));
    expect(callback).toHaveBeenCalledWith(true);
    
    cleanup();
  });

  it('onBackButton is no-op on web (non-android)', () => {
    const callback = vi.fn();
    const cleanup = appLifecycle.onBackButton(callback);
    expect(typeof cleanup).toBe('function');
    cleanup();
    expect(callback).not.toHaveBeenCalled();
  });
});

describe('initCapacitor', () => {
  it('does not throw on web', async () => {
    await expect(initCapacitor()).resolves.toBeUndefined();
  });
});

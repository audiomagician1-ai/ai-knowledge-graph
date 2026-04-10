/**
 * useDashboardPrefs — Persist user preferences for Dashboard widget sections.
 *
 * Features:
 * - Toggle section visibility (show/hide)
 * - Reorder sections (move up/down)
 * - Persisted to localStorage
 * - Reset to defaults
 */
import { useCallback, useSyncExternalStore } from 'react';

export interface SectionPref {
  id: string;
  visible: boolean;
}

const STORAGE_KEY = 'akg-dashboard-prefs';

const DEFAULT_SECTIONS: SectionPref[] = [
  { id: 'learning', visible: true },
  { id: 'analytics', visible: true },
  { id: 'domains', visible: true },
  { id: 'social', visible: true },
  { id: 'content', visible: true },
];

// ── In-memory cache + subscribers (useSyncExternalStore pattern) ──
let cached: SectionPref[] | null = null;
const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((l) => l());
}

function readFromStorage(): SectionPref[] {
  if (cached) return cached;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as SectionPref[];
      // Merge with defaults (handle new sections added in future)
      const known = new Set(parsed.map((s) => s.id));
      const merged = [...parsed];
      for (const def of DEFAULT_SECTIONS) {
        if (!known.has(def.id)) merged.push(def);
      }
      cached = merged;
      return merged;
    }
  } catch { /* ignore */ }
  cached = DEFAULT_SECTIONS;
  return DEFAULT_SECTIONS;
}

function writeToStorage(prefs: SectionPref[]) {
  cached = prefs;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  } catch { /* quota exceeded — ignore */ }
  notify();
}

function subscribe(cb: () => void) {
  listeners.add(cb);
  return () => { listeners.delete(cb); };
}

function getSnapshot(): SectionPref[] {
  return readFromStorage();
}

export function useDashboardPrefs() {
  const sections = useSyncExternalStore(subscribe, getSnapshot, getSnapshot);

  const toggleSection = useCallback((id: string) => {
    const current = readFromStorage();
    writeToStorage(current.map((s) => (s.id === id ? { ...s, visible: !s.visible } : s)));
  }, []);

  const moveSection = useCallback((id: string, direction: 'up' | 'down') => {
    const current = [...readFromStorage()];
    const idx = current.findIndex((s) => s.id === id);
    if (idx < 0) return;
    const swap = direction === 'up' ? idx - 1 : idx + 1;
    if (swap < 0 || swap >= current.length) return;
    [current[idx], current[swap]] = [current[swap], current[idx]];
    writeToStorage(current);
  }, []);

  const resetToDefaults = useCallback(() => {
    writeToStorage([...DEFAULT_SECTIONS]);
  }, []);

  return { sections, toggleSection, moveSection, resetToDefaults };
}

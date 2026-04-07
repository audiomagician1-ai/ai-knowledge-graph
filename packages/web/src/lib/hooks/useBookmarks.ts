import { useCallback, useMemo, useSyncExternalStore } from 'react';

const STORAGE_KEY = 'akg-bookmarks';

/**
 * useBookmarks — Manage a list of bookmarked concept IDs.
 *
 * Bookmarks persist in localStorage and allow quick access to saved concepts.
 * Think of it as a "read later" or "study later" list.
 */

interface BookmarkEntry {
  conceptId: string;
  domainId: string;
  label: string;
  addedAt: number;
}

function getStore(): BookmarkEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function setStore(bookmarks: BookmarkEntry[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(bookmarks));
  // Notify subscribers
  window.dispatchEvent(new Event('bookmarks-changed'));
}

let cache: BookmarkEntry[] | null = null;

function subscribe(callback: () => void) {
  const handler = () => {
    cache = null;
    callback();
  };
  window.addEventListener('bookmarks-changed', handler);
  window.addEventListener('storage', handler);
  return () => {
    window.removeEventListener('bookmarks-changed', handler);
    window.removeEventListener('storage', handler);
  };
}

function getSnapshot(): BookmarkEntry[] {
  if (cache === null) cache = getStore();
  return cache;
}

export function useBookmarks() {
  const bookmarks = useSyncExternalStore(subscribe, getSnapshot);

  const isBookmarked = useCallback(
    (conceptId: string) => bookmarks.some((b) => b.conceptId === conceptId),
    [bookmarks]
  );

  const toggle = useCallback(
    (conceptId: string, domainId: string, label: string) => {
      const current = getStore();
      const idx = current.findIndex((b) => b.conceptId === conceptId);

      if (idx >= 0) {
        // Remove
        current.splice(idx, 1);
      } else {
        // Add (max 100 bookmarks)
        current.unshift({
          conceptId,
          domainId,
          label,
          addedAt: Date.now(),
        });
        if (current.length > 100) current.pop();
      }

      setStore(current);
    },
    []
  );

  const remove = useCallback((conceptId: string) => {
    const current = getStore().filter((b) => b.conceptId !== conceptId);
    setStore(current);
  }, []);

  const clear = useCallback(() => {
    setStore([]);
  }, []);

  const count = useMemo(() => bookmarks.length, [bookmarks]);

  return { bookmarks, isBookmarked, toggle, remove, clear, count };
}

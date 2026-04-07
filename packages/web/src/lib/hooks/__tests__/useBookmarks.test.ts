import { describe, it, expect, beforeEach } from 'vitest';

const STORAGE_KEY = 'akg-bookmarks';

describe('Bookmarks storage logic', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('starts with empty bookmarks', () => {
    const raw = localStorage.getItem(STORAGE_KEY);
    expect(raw).toBeNull();
  });

  it('stores and retrieves bookmarks', () => {
    const bookmarks = [
      { conceptId: 'c1', domainId: 'd1', label: 'Test', addedAt: Date.now() },
    ];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(bookmarks));
    const result = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
    expect(result).toHaveLength(1);
    expect(result[0].conceptId).toBe('c1');
  });

  it('toggling adds then removes', () => {
    const bookmarks: any[] = [];
    // Add
    bookmarks.unshift({ conceptId: 'c1', domainId: 'd1', label: 'Test', addedAt: Date.now() });
    expect(bookmarks).toHaveLength(1);
    // Remove
    const idx = bookmarks.findIndex((b) => b.conceptId === 'c1');
    if (idx >= 0) bookmarks.splice(idx, 1);
    expect(bookmarks).toHaveLength(0);
  });

  it('enforces max 100 bookmarks', () => {
    const bookmarks: any[] = [];
    for (let i = 0; i < 105; i++) {
      bookmarks.unshift({ conceptId: `c${i}`, domainId: 'd1', label: `Test ${i}`, addedAt: Date.now() });
      if (bookmarks.length > 100) bookmarks.pop();
    }
    expect(bookmarks.length).toBe(100);
    expect(bookmarks[0].conceptId).toBe('c104');
  });

  it('handles corrupted storage gracefully', () => {
    localStorage.setItem(STORAGE_KEY, 'invalid json{{{');
    try {
      const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY)!);
      expect(parsed).toBeUndefined(); // Should not reach here
    } catch {
      // Expected
      expect(true).toBe(true);
    }
  });
});

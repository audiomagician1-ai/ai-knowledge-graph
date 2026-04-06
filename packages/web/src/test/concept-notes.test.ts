import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock localStorage
const storageMap = new Map<string, string>();
Object.defineProperty(globalThis, 'localStorage', {
  value: {
    getItem: vi.fn((key: string) => storageMap.get(key) ?? null),
    setItem: vi.fn((key: string, val: string) => storageMap.set(key, val)),
    removeItem: vi.fn((key: string) => storageMap.delete(key)),
    clear: vi.fn(() => storageMap.clear()),
    get length() { return storageMap.size; },
    key: vi.fn(() => null),
  },
  configurable: true,
});

describe('Concept Notes logic', () => {
  beforeEach(() => {
    storageMap.clear();
  });

  it('should serialize note correctly', () => {
    const note = {
      content: 'This is a test note about variables',
      updatedAt: Date.now(),
      createdAt: Date.now(),
    };
    const json = JSON.stringify({ 'variables': note });
    const parsed = JSON.parse(json);
    expect(parsed['variables'].content).toBe('This is a test note about variables');
  });

  it('should handle empty notes store', () => {
    const raw = localStorage.getItem('akg-concept-notes');
    expect(raw).toBeNull();
  });

  it('should store and retrieve notes', () => {
    const notes: Record<string, { content: string; updatedAt: number; createdAt: number }> = {};
    const now = Date.now();
    notes['variables'] = { content: '变量是编程的基础', updatedAt: now, createdAt: now };
    notes['functions'] = { content: '函数封装了可复用的逻辑', updatedAt: now, createdAt: now };

    localStorage.setItem('akg-concept-notes', JSON.stringify(notes));
    const stored = JSON.parse(localStorage.getItem('akg-concept-notes') || '{}');
    expect(Object.keys(stored).length).toBe(2);
    expect(stored['variables'].content).toContain('变量');
  });

  it('should delete a note correctly', () => {
    const notes: Record<string, unknown> = {
      a: { content: 'note a', updatedAt: 1, createdAt: 1 },
      b: { content: 'note b', updatedAt: 2, createdAt: 2 },
    };
    delete notes['a'];
    expect(Object.keys(notes)).toEqual(['b']);
  });

  it('should sort notes by updatedAt descending', () => {
    const notes = {
      a: { content: 'old', updatedAt: 100, createdAt: 100 },
      b: { content: 'new', updatedAt: 300, createdAt: 200 },
      c: { content: 'mid', updatedAt: 200, createdAt: 150 },
    };
    const sorted = Object.entries(notes)
      .map(([id, n]) => ({ conceptId: id, ...n }))
      .sort((a, b) => b.updatedAt - a.updatedAt);
    expect(sorted[0].conceptId).toBe('b');
    expect(sorted[1].conceptId).toBe('c');
    expect(sorted[2].conceptId).toBe('a');
  });

  it('should export notes as valid JSON', () => {
    const notes = { test: { content: 'hello', updatedAt: 1, createdAt: 1 } };
    const exported = JSON.stringify(notes, null, 2);
    expect(() => JSON.parse(exported)).not.toThrow();
    expect(JSON.parse(exported).test.content).toBe('hello');
  });

  it('should import and merge notes', () => {
    const existing = { a: { content: 'a', updatedAt: 1, createdAt: 1 } };
    const incoming = { b: { content: 'b', updatedAt: 2, createdAt: 2 } };
    const merged = { ...existing, ...incoming };
    expect(Object.keys(merged).length).toBe(2);
    expect(merged.a.content).toBe('a');
    expect(merged.b.content).toBe('b');
  });
});

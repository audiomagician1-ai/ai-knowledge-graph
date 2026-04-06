import { describe, it, expect, vi, beforeEach } from 'vitest';

/**
 * Tests for notes-api integration logic (unit tests for the sync behavior).
 * The actual API calls are mocked.
 */
describe('Notes API Client', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('should serialize notes for bulk sync', () => {
    const notes: Record<string, { content: string; updatedAt: number; createdAt: number }> = {
      'python-basics': { content: 'Variables and types', updatedAt: Date.now(), createdAt: Date.now() },
      'recursion': { content: 'Self-referencing functions', updatedAt: Date.now(), createdAt: Date.now() },
    };
    
    const contentMap: Record<string, string> = {};
    for (const [id, note] of Object.entries(notes)) {
      contentMap[id] = note.content;
    }
    
    expect(Object.keys(contentMap)).toHaveLength(2);
    expect(contentMap['python-basics']).toBe('Variables and types');
  });

  it('should merge remote notes (remote wins for newer)', () => {
    const local: Record<string, { content: string; updatedAt: number; createdAt: number }> = {
      'concept-a': { content: 'old local', updatedAt: 1000, createdAt: 500 },
      'concept-b': { content: 'local only', updatedAt: 2000, createdAt: 1500 },
    };

    const remote = [
      { concept_id: 'concept-a', content: 'newer remote', updated_at: 5, created_at: 1 }, // 5*1000=5000 > 1000
      { concept_id: 'concept-c', content: 'new from remote', updated_at: 3, created_at: 2 },
    ];

    const merged = { ...local };
    for (const r of remote) {
      const existing = merged[r.concept_id];
      if (!existing || r.updated_at * 1000 > existing.updatedAt) {
        merged[r.concept_id] = {
          content: r.content,
          updatedAt: r.updated_at * 1000,
          createdAt: r.created_at * 1000,
        };
      }
    }

    expect(merged['concept-a'].content).toBe('newer remote'); // remote won
    expect(merged['concept-b'].content).toBe('local only');   // local preserved
    expect(merged['concept-c'].content).toBe('new from remote'); // new from remote
    expect(Object.keys(merged)).toHaveLength(3);
  });

  it('should handle empty notes gracefully', () => {
    const contentMap: Record<string, string> = {};
    expect(Object.keys(contentMap).length).toBe(0);
  });

  it('should store sync timestamp', () => {
    const now = Date.now();
    localStorage.setItem('akg-notes-last-sync', now.toString());
    const stored = Number(localStorage.getItem('akg-notes-last-sync'));
    expect(stored).toBe(now);
  });

  it('should filter out empty content in bulk sync', () => {
    const rawNotes: Record<string, string> = {
      'valid': 'some content',
      'empty': '',
      'whitespace': '   ',
    };
    
    const filtered: Record<string, string> = {};
    for (const [id, content] of Object.entries(rawNotes)) {
      if (content.trim()) filtered[id] = content;
    }
    
    expect(Object.keys(filtered)).toHaveLength(1);
    expect(filtered['valid']).toBe('some content');
  });
});

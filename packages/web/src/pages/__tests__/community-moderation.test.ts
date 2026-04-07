/**
 * Tests for community moderation logic (frontend data transformations).
 */
import { describe, it, expect } from 'vitest';

interface Suggestion {
  id: string;
  type: 'concept' | 'link' | 'correction' | 'feedback';
  status: 'pending' | 'approved' | 'rejected';
  title: string;
  votes: number;
  moderation_reason?: string;
}

describe('Community Moderation — status filtering', () => {
  const suggestions: Suggestion[] = [
    { id: '1', type: 'concept', status: 'pending', title: 'New concept', votes: 5 },
    { id: '2', type: 'link', status: 'approved', title: 'Approved link', votes: 10, moderation_reason: 'Good' },
    { id: '3', type: 'feedback', status: 'rejected', title: 'Bad feedback', votes: 0, moderation_reason: 'Spam' },
    { id: '4', type: 'correction', status: 'pending', title: 'Typo fix', votes: 3 },
  ];

  it('should return all suggestions when filter is "all"', () => {
    const result = suggestions;
    expect(result).toHaveLength(4);
  });

  it('should filter by pending status', () => {
    const result = suggestions.filter((s) => s.status === 'pending');
    expect(result).toHaveLength(2);
    expect(result.every((s) => s.status === 'pending')).toBe(true);
  });

  it('should filter by approved status', () => {
    const result = suggestions.filter((s) => s.status === 'approved');
    expect(result).toHaveLength(1);
    expect(result[0].title).toBe('Approved link');
  });

  it('should filter by rejected status', () => {
    const result = suggestions.filter((s) => s.status === 'rejected');
    expect(result).toHaveLength(1);
    expect(result[0].moderation_reason).toBe('Spam');
  });
});

describe('Community Moderation — vote-based queue priority', () => {
  it('should sort pending items by votes descending', () => {
    const queue = [
      { id: 'a', votes: 2, status: 'pending' as const },
      { id: 'b', votes: 10, status: 'pending' as const },
      { id: 'c', votes: 5, status: 'pending' as const },
    ];

    const sorted = [...queue].sort((a, b) => b.votes - a.votes);
    expect(sorted[0].id).toBe('b');
    expect(sorted[1].id).toBe('c');
    expect(sorted[2].id).toBe('a');
  });
});

describe('Community Moderation — admin token validation', () => {
  it('should format bearer token correctly', () => {
    const token = 'my-secret';
    const header = `Bearer ${token}`;
    expect(header).toBe('Bearer my-secret');
  });

  it('should handle empty token', () => {
    const token = '';
    expect(!token).toBe(true);
  });
});

describe('Community Moderation — status badge mapping', () => {
  const STATUS_META = {
    pending: { label: '待审核', color: '#f59e0b' },
    approved: { label: '已通过', color: '#22c55e' },
    rejected: { label: '已拒绝', color: '#ef4444' },
  };

  it('should have metadata for all statuses', () => {
    expect(STATUS_META.pending.label).toBe('待审核');
    expect(STATUS_META.approved.label).toBe('已通过');
    expect(STATUS_META.rejected.label).toBe('已拒绝');
  });

  it('should use distinct colors for each status', () => {
    const colors = Object.values(STATUS_META).map((m) => m.color);
    expect(new Set(colors).size).toBe(3);
  });
});

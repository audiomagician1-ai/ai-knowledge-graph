/**
 * Tests for RecentActivity logic — formatTimeAgo and deduplication.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

function formatTimeAgo(ts: number, now: number): string {
  const diff = now - ts;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  return new Date(ts).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

describe('formatTimeAgo', () => {
  const now = 1712505600000; // 2024-04-07T20:00:00Z

  it('returns 刚刚 for <1 minute', () => {
    expect(formatTimeAgo(now - 30000, now)).toBe('刚刚');
  });

  it('returns minutes for <1 hour', () => {
    expect(formatTimeAgo(now - 300000, now)).toBe('5分钟前');
    expect(formatTimeAgo(now - 2700000, now)).toBe('45分钟前');
  });

  it('returns hours for <24 hours', () => {
    expect(formatTimeAgo(now - 3600000, now)).toBe('1小时前');
    expect(formatTimeAgo(now - 7200000, now)).toBe('2小时前');
  });

  it('returns days for <7 days', () => {
    expect(formatTimeAgo(now - 86400000, now)).toBe('1天前');
    expect(formatTimeAgo(now - 259200000, now)).toBe('3天前');
  });
});

describe('Activity deduplication', () => {
  interface Activity { conceptId: string; timestamp: number; type: string }

  function deduplicate(items: Activity[]): Activity[] {
    items.sort((a, b) => b.timestamp - a.timestamp);
    const seen = new Set<string>();
    const result: Activity[] = [];
    for (const item of items) {
      if (!seen.has(item.conceptId)) {
        seen.add(item.conceptId);
        result.push(item);
      }
    }
    return result;
  }

  it('keeps most recent action per concept', () => {
    const items: Activity[] = [
      { conceptId: 'a', timestamp: 100, type: 'started' },
      { conceptId: 'a', timestamp: 200, type: 'mastered' },
      { conceptId: 'b', timestamp: 150, type: 'started' },
    ];
    const result = deduplicate(items);
    expect(result).toHaveLength(2);
    expect(result[0].conceptId).toBe('a');
    expect(result[0].type).toBe('mastered'); // most recent
    expect(result[1].conceptId).toBe('b');
  });

  it('handles empty list', () => {
    expect(deduplicate([])).toHaveLength(0);
  });

  it('handles single item', () => {
    expect(deduplicate([{ conceptId: 'a', timestamp: 100, type: 'started' }])).toHaveLength(1);
  });
});

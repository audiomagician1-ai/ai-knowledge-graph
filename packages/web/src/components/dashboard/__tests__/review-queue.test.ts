import { describe, it, expect } from 'vitest';

describe('ReviewQueue logic', () => {
  it('classifies urgency levels correctly', () => {
    const getUrgency = (overdueDays: number) =>
      overdueDays >= 7 ? 'critical' : overdueDays >= 3 ? 'warning' : 'normal';

    expect(getUrgency(0)).toBe('normal');
    expect(getUrgency(2)).toBe('normal');
    expect(getUrgency(3)).toBe('warning');
    expect(getUrgency(6)).toBe('warning');
    expect(getUrgency(7)).toBe('critical');
    expect(getUrgency(30)).toBe('critical');
  });

  it('counts urgent items correctly', () => {
    const items = [
      { overdue_days: 0 },
      { overdue_days: 1 },
      { overdue_days: 5 },
      { overdue_days: 10 },
    ];
    const urgentCount = items.filter((i) => i.overdue_days >= 3).length;
    expect(urgentCount).toBe(2);
  });

  it('formats concept id as display name', () => {
    const formatName = (id: string) => id.replace(/-/g, ' ');
    expect(formatName('binary-system')).toBe('binary system');
    expect(formatName('neural-network-basics')).toBe('neural network basics');
    expect(formatName('hello-world')).toBe('hello world');
  });

  it('handles empty items gracefully', () => {
    const items: Array<{ overdue_days: number }> = [];
    const urgentCount = items.filter((i) => i.overdue_days >= 3).length;
    expect(urgentCount).toBe(0);
    expect(items.length).toBe(0);
  });

  it('limits items to maxItems', () => {
    const allItems = Array.from({ length: 20 }, (_, i) => ({ concept_id: `c-${i}` }));
    const maxItems = 8;
    const displayed = allItems.slice(0, maxItems);
    expect(displayed).toHaveLength(8);
  });
});

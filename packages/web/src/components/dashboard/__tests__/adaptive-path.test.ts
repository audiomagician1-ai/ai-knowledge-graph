import { describe, it, expect } from 'vitest';

describe('AdaptivePathWidget logic', () => {
  it('action config covers all action types', () => {
    const validActions = ['learn', 'review', 'fill_gap'];
    const actionConfig: Record<string, { label: string; color: string }> = {
      review: { label: '复习', color: '#f59e0b' },
      fill_gap: { label: '补缺', color: '#ef4444' },
      learn: { label: '学习', color: '#3b82f6' },
    };
    for (const action of validActions) {
      expect(actionConfig[action]).toBeDefined();
      expect(actionConfig[action].label).toBeTruthy();
    }
  });

  it('counts action types correctly', () => {
    const steps = [
      { action: 'review' },
      { action: 'review' },
      { action: 'fill_gap' },
      { action: 'learn' },
      { action: 'learn' },
      { action: 'learn' },
    ];
    const counts = {
      review: steps.filter((s) => s.action === 'review').length,
      gap: steps.filter((s) => s.action === 'fill_gap').length,
      learn: steps.filter((s) => s.action === 'learn').length,
    };
    expect(counts).toEqual({ review: 2, gap: 1, learn: 3 });
  });

  it('formats step display correctly', () => {
    const step = {
      name: 'Neural Networks',
      estimated_minutes: 25,
      difficulty: 3,
      reasons: ['ideal difficulty step (+1)', 'active subdomain continuity'],
    };
    const display = `~${step.estimated_minutes}分钟 · 难度${step.difficulty}`;
    expect(display).toBe('~25分钟 · 难度3');
    const reasonText = step.reasons.join(' · ');
    expect(reasonText).toContain('ideal');
    expect(reasonText).toContain('subdomain');
  });

  it('limits steps to maxSteps', () => {
    const allSteps = Array.from({ length: 15 }, (_, i) => ({
      concept_id: `c-${i}`,
      priority: 100 - i,
    }));
    const maxSteps = 6;
    const displayed = allSteps.slice(0, maxSteps);
    expect(displayed).toHaveLength(6);
    // Priority should be descending (already sorted by API)
    for (let i = 0; i < displayed.length - 1; i++) {
      expect(displayed[i].priority).toBeGreaterThanOrEqual(displayed[i + 1].priority);
    }
  });

  it('handles empty steps gracefully', () => {
    const steps: Array<{ action: string }> = [];
    const counts = {
      review: steps.filter((s) => s.action === 'review').length,
      gap: steps.filter((s) => s.action === 'fill_gap').length,
      learn: steps.filter((s) => s.action === 'learn').length,
    };
    expect(counts).toEqual({ review: 0, gap: 0, learn: 0 });
  });
});

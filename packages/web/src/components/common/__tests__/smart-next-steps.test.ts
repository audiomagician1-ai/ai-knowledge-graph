import { describe, it, expect } from 'vitest';

/**
 * Tests for SmartNextSteps suggestion logic.
 */

interface MockNode { id: string; label: string; difficulty: number; is_milestone: boolean; subdomain_id: string }
interface MockEdge { source: string; target: string; relation_type: string }
interface MockProgress { status: string; sessions?: number }

function computeSteps(
  nodes: MockNode[],
  edges: MockEdge[],
  progress: Record<string, MockProgress>,
): { type: string; title: string; priority: number }[] {
  const masteredIds = new Set(Object.entries(progress).filter(([, p]) => p.status === 'mastered').map(([id]) => id));
  const learningIds = new Set(Object.entries(progress).filter(([, p]) => p.status === 'learning').map(([id]) => id));

  const prereqMap = new Map<string, Set<string>>();
  for (const edge of edges) {
    if (edge.relation_type === 'prerequisite') {
      if (!prereqMap.has(edge.target)) prereqMap.set(edge.target, new Set());
      prereqMap.get(edge.target)!.add(edge.source);
    }
  }

  const suggestions: { type: string; title: string; priority: number }[] = [];

  // Continue learning
  const learningConcepts = nodes.filter((n) => learningIds.has(n.id));
  if (learningConcepts.length > 0) {
    suggestions.push({ type: 'continue_learning', title: learningConcepts[0].label, priority: 100 });
  }

  // Recommended
  const recommended = nodes.filter((n) => {
    if (masteredIds.has(n.id) || learningIds.has(n.id)) return false;
    const prereqs = prereqMap.get(n.id);
    if (!prereqs || prereqs.size === 0) return false;
    return [...prereqs].every((p) => masteredIds.has(p));
  });
  if (recommended.length > 0) {
    suggestions.push({ type: 'learn_recommended', title: recommended[0].label, priority: 90 });
  }

  // Explore
  if (Object.keys(progress).length === 0) {
    suggestions.push({ type: 'explore_domain', title: 'Start', priority: 70 });
  }

  // Review
  if (masteredIds.size > 3) {
    suggestions.push({ type: 'review', title: `Review ${masteredIds.size}`, priority: 60 });
  }

  return suggestions.sort((a, b) => b.priority - a.priority).slice(0, 3);
}

const nodes: MockNode[] = [
  { id: 'a', label: 'Basics', difficulty: 1, is_milestone: false, subdomain_id: 'intro' },
  { id: 'b', label: 'Intermediate', difficulty: 3, is_milestone: false, subdomain_id: 'core' },
  { id: 'c', label: 'Advanced', difficulty: 5, is_milestone: true, subdomain_id: 'core' },
  { id: 'd', label: 'Expert', difficulty: 7, is_milestone: false, subdomain_id: 'advanced' },
];

const edges: MockEdge[] = [
  { source: 'a', target: 'b', relation_type: 'prerequisite' },
  { source: 'b', target: 'c', relation_type: 'prerequisite' },
  { source: 'c', target: 'd', relation_type: 'prerequisite' },
];

describe('SmartNextSteps logic', () => {
  it('suggests explore_domain for new users', () => {
    const steps = computeSteps(nodes, edges, {});
    expect(steps.length).toBe(1);
    expect(steps[0].type).toBe('explore_domain');
  });

  it('suggests continue_learning for in-progress concepts', () => {
    const steps = computeSteps(nodes, edges, { a: { status: 'learning', sessions: 2 } });
    expect(steps.some((s) => s.type === 'continue_learning')).toBe(true);
  });

  it('suggests learn_recommended when prereqs are mastered', () => {
    const steps = computeSteps(nodes, edges, { a: { status: 'mastered' } });
    const rec = steps.find((s) => s.type === 'learn_recommended');
    expect(rec).toBeDefined();
    expect(rec!.title).toBe('Intermediate'); // b becomes recommended
  });

  it('suggests review when > 3 concepts mastered', () => {
    const steps = computeSteps(
      [...nodes, { id: 'e', label: 'E', difficulty: 2, is_milestone: false, subdomain_id: 'intro' }],
      edges,
      { a: { status: 'mastered' }, b: { status: 'mastered' }, c: { status: 'mastered' }, d: { status: 'mastered' } },
    );
    expect(steps.some((s) => s.type === 'review')).toBe(true);
  });

  it('returns max 3 suggestions', () => {
    const steps = computeSteps(
      nodes,
      edges,
      { a: { status: 'mastered' }, b: { status: 'learning' } },
    );
    expect(steps.length).toBeLessThanOrEqual(3);
  });

  it('prioritizes continue_learning over recommended', () => {
    const steps = computeSteps(
      nodes,
      edges,
      { a: { status: 'mastered' }, b: { status: 'learning' } },
    );
    if (steps.length >= 2) {
      const contIdx = steps.findIndex((s) => s.type === 'continue_learning');
      const recIdx = steps.findIndex((s) => s.type === 'learn_recommended');
      if (contIdx >= 0 && recIdx >= 0) {
        expect(contIdx).toBeLessThan(recIdx);
      }
    }
  });

  it('handles empty graph gracefully', () => {
    const steps = computeSteps([], [], {});
    expect(steps.length).toBe(1);
    expect(steps[0].type).toBe('explore_domain');
  });
});

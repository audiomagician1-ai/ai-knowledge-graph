import { describe, it, expect } from 'vitest';
import { baseSize, nodeColor, type GNode } from '../components/graph/graph-visual-utils';

const makeGNode = (opts: Partial<GNode> = {}): GNode => ({
  id: 'test', label: 'Test', domain_id: 'd', subdomain_id: 's',
  difficulty: 5, status: 'not_started', is_milestone: false,
  ...opts,
} as GNode);

describe('graph-visual-utils', () => {
  describe('baseSize', () => {
    it('returns larger size for milestones', () => {
      const normal = baseSize(makeGNode({ difficulty: 5 }));
      const milestone = baseSize(makeGNode({ difficulty: 5, is_milestone: true }));
      expect(milestone).toBeGreaterThan(normal);
    });

    it('scales with difficulty', () => {
      const easy = baseSize(makeGNode({ difficulty: 1 }));
      const hard = baseSize(makeGNode({ difficulty: 10 }));
      expect(hard).toBeGreaterThan(easy);
    });

    it('returns minimum for difficulty 0', () => {
      const size = baseSize(makeGNode({ difficulty: 0 }));
      expect(size).toBeGreaterThan(0);
      expect(size).toBeLessThan(1);
    });
  });

  describe('nodeColor', () => {
    it('returns emerald for mastered', () => {
      expect(nodeColor(makeGNode({ status: 'mastered' }))).toBe('#10b981');
    });

    it('returns amber for learning', () => {
      expect(nodeColor(makeGNode({ status: 'learning' }))).toBe('#f59e0b');
    });

    it('returns cyan for recommended', () => {
      expect(nodeColor(makeGNode({ is_recommended: true }))).toBe('#06b6d4');
    });

    it('returns difficulty color for default status', () => {
      const color = nodeColor(makeGNode({ difficulty: 5 }));
      expect(color).toBeTruthy();
      expect(color).not.toBe('#10b981');
      expect(color).not.toBe('#f59e0b');
    });

    it('mastered takes priority over recommended', () => {
      expect(nodeColor(makeGNode({ status: 'mastered', is_recommended: true }))).toBe('#10b981');
    });
  });
});

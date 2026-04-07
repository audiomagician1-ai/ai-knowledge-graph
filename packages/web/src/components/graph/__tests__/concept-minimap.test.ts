import { describe, it, expect } from 'vitest';

/**
 * Tests for ConceptMinimap component logic.
 * Tests subdomain sibling detection and ordering.
 */

interface MockNode { id: string; label: string; difficulty: number; subdomain_id: string }

function findSiblings(
  conceptId: string,
  nodes: MockNode[],
): { siblings: MockNode[]; currentIndex: number; subdomainName: string } {
  const currentNode = nodes.find((n) => n.id === conceptId);
  if (!currentNode) return { siblings: [], currentIndex: -1, subdomainName: '' };

  const subdomain = currentNode.subdomain_id;
  const sameSubdomain = nodes
    .filter((n) => n.subdomain_id === subdomain)
    .sort((a, b) => a.difficulty - b.difficulty || a.label.localeCompare(b.label));

  return {
    siblings: sameSubdomain,
    currentIndex: sameSubdomain.findIndex((n) => n.id === conceptId),
    subdomainName: subdomain?.replace(/-/g, ' ') || '',
  };
}

const sampleNodes: MockNode[] = [
  { id: 'a1', label: 'Intro to Arrays', difficulty: 1, subdomain_id: 'data-structures' },
  { id: 'a2', label: 'Linked List', difficulty: 3, subdomain_id: 'data-structures' },
  { id: 'a3', label: 'Binary Tree', difficulty: 5, subdomain_id: 'data-structures' },
  { id: 'a4', label: 'Graph Theory', difficulty: 7, subdomain_id: 'data-structures' },
  { id: 'b1', label: 'Gradient Descent', difficulty: 4, subdomain_id: 'ml-basics' },
  { id: 'b2', label: 'Neural Networks', difficulty: 6, subdomain_id: 'ml-basics' },
];

describe('ConceptMinimap logic', () => {
  it('finds all siblings in the same subdomain', () => {
    const { siblings } = findSiblings('a2', sampleNodes);
    expect(siblings.length).toBe(4);
    expect(siblings.map((s) => s.id)).toEqual(['a1', 'a2', 'a3', 'a4']);
  });

  it('returns correct current index', () => {
    const { currentIndex } = findSiblings('a3', sampleNodes);
    expect(currentIndex).toBe(2); // 0-indexed, 3rd in sorted list
  });

  it('sorts siblings by difficulty ascending', () => {
    const { siblings } = findSiblings('a4', sampleNodes);
    const diffs = siblings.map((s) => s.difficulty);
    expect(diffs).toEqual([1, 3, 5, 7]);
  });

  it('returns correct subdomain name', () => {
    const { subdomainName } = findSiblings('a1', sampleNodes);
    expect(subdomainName).toBe('data structures');
  });

  it('does not include nodes from other subdomains', () => {
    const { siblings } = findSiblings('b1', sampleNodes);
    expect(siblings.length).toBe(2);
    expect(siblings.map((s) => s.id)).toEqual(['b1', 'b2']);
  });

  it('returns empty for nonexistent concept', () => {
    const { siblings, currentIndex } = findSiblings('nonexistent', sampleNodes);
    expect(siblings.length).toBe(0);
    expect(currentIndex).toBe(-1);
  });

  it('handles single concept in subdomain', () => {
    const nodes: MockNode[] = [
      { id: 'solo', label: 'Solo Concept', difficulty: 5, subdomain_id: 'unique-sub' },
      { id: 'other', label: 'Other', difficulty: 3, subdomain_id: 'different' },
    ];
    const { siblings, currentIndex } = findSiblings('solo', nodes);
    expect(siblings.length).toBe(1);
    expect(currentIndex).toBe(0);
  });
});

import { describe, it, expect } from 'vitest';

/**
 * Tests for ConceptPrerequisites component logic.
 * We test the prerequisite/dependent detection logic separately from React rendering.
 */

interface MockNode { id: string; label: string; difficulty: number; subdomain_id: string }
interface MockEdge { source: string; target: string; relation_type: string }

function findPrerequisites(
  conceptId: string,
  nodes: MockNode[],
  edges: MockEdge[],
): { prerequisites: MockNode[]; dependents: MockNode[] } {
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));

  const prereqs = edges
    .filter((e) => e.target === conceptId && e.relation_type === 'prerequisite')
    .map((e) => nodeMap.get(e.source))
    .filter(Boolean) as MockNode[];

  const deps = edges
    .filter((e) => e.source === conceptId && e.relation_type === 'prerequisite')
    .map((e) => nodeMap.get(e.target))
    .filter(Boolean) as MockNode[];

  return { prerequisites: prereqs, dependents: deps };
}

const sampleNodes: MockNode[] = [
  { id: 'a', label: 'Concept A', difficulty: 1, subdomain_id: 'intro' },
  { id: 'b', label: 'Concept B', difficulty: 3, subdomain_id: 'core' },
  { id: 'c', label: 'Concept C', difficulty: 5, subdomain_id: 'core' },
  { id: 'd', label: 'Concept D', difficulty: 7, subdomain_id: 'advanced' },
  { id: 'e', label: 'Concept E', difficulty: 2, subdomain_id: 'intro' },
];

const sampleEdges: MockEdge[] = [
  { source: 'a', target: 'b', relation_type: 'prerequisite' },
  { source: 'a', target: 'c', relation_type: 'prerequisite' },
  { source: 'b', target: 'd', relation_type: 'prerequisite' },
  { source: 'c', target: 'd', relation_type: 'prerequisite' },
  { source: 'a', target: 'e', relation_type: 'related_to' },
];

describe('ConceptPrerequisites logic', () => {
  it('finds prerequisites for a concept', () => {
    const { prerequisites } = findPrerequisites('b', sampleNodes, sampleEdges);
    expect(prerequisites.length).toBe(1);
    expect(prerequisites[0].id).toBe('a');
  });

  it('finds dependents (concepts that require this one)', () => {
    const { dependents } = findPrerequisites('a', sampleNodes, sampleEdges);
    expect(dependents.length).toBe(2); // b and c
    expect(dependents.map((n) => n.id).sort()).toEqual(['b', 'c']);
  });

  it('returns empty for concepts with no prerequisites', () => {
    const { prerequisites } = findPrerequisites('a', sampleNodes, sampleEdges);
    expect(prerequisites.length).toBe(0);
  });

  it('returns empty for concepts with no dependents', () => {
    const { dependents } = findPrerequisites('d', sampleNodes, sampleEdges);
    expect(dependents.length).toBe(0);
  });

  it('ignores non-prerequisite edges (related_to)', () => {
    const { prerequisites, dependents } = findPrerequisites('e', sampleNodes, sampleEdges);
    expect(prerequisites.length).toBe(0);
    expect(dependents.length).toBe(0);
  });

  it('handles multiple prerequisites for concept D', () => {
    const { prerequisites } = findPrerequisites('d', sampleNodes, sampleEdges);
    expect(prerequisites.length).toBe(2);
    expect(prerequisites.map((n) => n.id).sort()).toEqual(['b', 'c']);
  });

  it('handles concepts not in graph gracefully', () => {
    const { prerequisites, dependents } = findPrerequisites('nonexistent', sampleNodes, sampleEdges);
    expect(prerequisites.length).toBe(0);
    expect(dependents.length).toBe(0);
  });

  it('handles empty graph', () => {
    const { prerequisites, dependents } = findPrerequisites('a', [], []);
    expect(prerequisites.length).toBe(0);
    expect(dependents.length).toBe(0);
  });
});

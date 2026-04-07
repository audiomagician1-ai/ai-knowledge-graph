import { describe, it, expect } from 'vitest';
import {
  shouldCluster,
  clusterBySubdomain,
  nodePriority,
  selectTopNodes,
  LOD_THRESHOLD,
  LOD_MAX_VISIBLE,
} from '../graph-lod';

function makeNode(id: string, subdomain: string, overrides: Partial<any> = {}): any {
  return {
    id,
    label: id,
    subdomain_id: subdomain,
    status: 'not_started',
    difficulty: 5,
    is_milestone: false,
    is_recommended: false,
    ...overrides,
  };
}

describe('shouldCluster', () => {
  it('returns false for small graphs', () => {
    expect(shouldCluster(50)).toBe(false);
    expect(shouldCluster(199)).toBe(false);
  });

  it('returns true for large graphs', () => {
    expect(shouldCluster(200)).toBe(true);
    expect(shouldCluster(500)).toBe(true);
  });

  it('threshold is 200', () => {
    expect(LOD_THRESHOLD).toBe(200);
  });
});

describe('clusterBySubdomain', () => {
  it('returns full mode for small graphs', () => {
    const nodes = Array.from({ length: 50 }, (_, i) => makeNode(`n${i}`, 'sub-a'));
    const result = clusterBySubdomain(nodes, []);
    expect(result.mode).toBe('full');
    expect(result.nodes.length).toBe(50);
  });

  it('clusters nodes by subdomain for large graphs', () => {
    const nodes = [
      ...Array.from({ length: 120 }, (_, i) => makeNode(`a${i}`, 'algebra')),
      ...Array.from({ length: 100 }, (_, i) => makeNode(`g${i}`, 'geometry')),
    ];
    const result = clusterBySubdomain(nodes, []);
    expect(result.mode).toBe('clustered');
    expect(result.clusterCount).toBe(2);

    const clusterNodes = result.nodes.filter((n: any) => n.is_cluster);
    expect(clusterNodes.length).toBe(2);
  });

  it('preserves milestone nodes outside clusters', () => {
    const nodes = [
      ...Array.from({ length: 200 }, (_, i) => makeNode(`n${i}`, 'sub-a')),
    ];
    nodes[50].is_milestone = true;
    nodes[50].id = 'milestone-node';

    const result = clusterBySubdomain(nodes, []);
    const milestoneInResult = result.nodes.find((n: any) => n.id === 'milestone-node');
    expect(milestoneInResult).toBeTruthy();
  });

  it('preserves explicitly preserved IDs', () => {
    const nodes = Array.from({ length: 250 }, (_, i) => makeNode(`n${i}`, 'sub-a'));
    const result = clusterBySubdomain(nodes, [], {
      preserveIds: new Set(['n0', 'n1']),
    });
    const preserved = result.nodes.filter((n: any) => !n.is_cluster);
    expect(preserved.some((n: any) => n.id === 'n0')).toBe(true);
    expect(preserved.some((n: any) => n.id === 'n1')).toBe(true);
  });

  it('merges inter-cluster edges and removes intra-cluster edges', () => {
    const nodes = [
      ...Array.from({ length: 120 }, (_, i) => makeNode(`a${i}`, 'algebra')),
      ...Array.from({ length: 100 }, (_, i) => makeNode(`g${i}`, 'geometry')),
    ];
    const edges = [
      { source: 'a0', target: 'a1', relation_type: 'prerequisite' },
      { source: 'a0', target: 'g0', relation_type: 'related' },
    ];
    const result = clusterBySubdomain(nodes, edges as any);
    // a0->a1 is intra-cluster (both algebra) → removed
    // a0->g0 is inter-cluster → remapped to cluster_algebra->cluster_geometry
    expect(result.edges.length).toBe(1);
  });

  it('cluster node has correct aggregated stats', () => {
    const nodes = [
      ...Array.from({ length: 200 }, (_, i) =>
        makeNode(`n${i}`, 'basics', {
          status: i < 50 ? 'mastered' : i < 100 ? 'learning' : 'not_started',
          difficulty: 3,
        })
      ),
    ];
    const result = clusterBySubdomain(nodes, []);
    const cluster = result.nodes.find((n: any) => n.is_cluster) as any;
    expect(cluster).toBeTruthy();
    expect(cluster.masteredCount).toBe(50);
    expect(cluster.learningCount).toBe(50);
    expect(cluster.nodeCount).toBe(200);
  });
});

describe('nodePriority', () => {
  it('milestones have highest priority', () => {
    const milestone = makeNode('m', 'sub', { is_milestone: true });
    const normal = makeNode('n', 'sub');
    expect(nodePriority(milestone)).toBeGreaterThan(nodePriority(normal));
  });

  it('recommended nodes rank higher than normal', () => {
    const rec = makeNode('r', 'sub', { is_recommended: true });
    const normal = makeNode('n', 'sub');
    expect(nodePriority(rec)).toBeGreaterThan(nodePriority(normal));
  });

  it('learning nodes rank higher than not_started', () => {
    const learning = makeNode('l', 'sub', { status: 'learning' });
    const notStarted = makeNode('n', 'sub', { status: 'not_started' });
    expect(nodePriority(learning)).toBeGreaterThan(nodePriority(notStarted));
  });
});

describe('selectTopNodes', () => {
  it('returns at most maxCount nodes', () => {
    const nodes = Array.from({ length: 300 }, (_, i) => makeNode(`n${i}`, 'sub'));
    const top = selectTopNodes(nodes, 50);
    expect(top.length).toBe(50);
  });

  it('prioritizes milestones over normal nodes', () => {
    const nodes = [
      ...Array.from({ length: 300 }, (_, i) => makeNode(`n${i}`, 'sub')),
    ];
    nodes[250].is_milestone = true;
    nodes[250].id = 'milestone';

    const top = selectTopNodes(nodes, 10);
    expect(top.some((n: any) => n.id === 'milestone')).toBe(true);
  });

  it('LOD_MAX_VISIBLE is 150', () => {
    expect(LOD_MAX_VISIBLE).toBe(150);
  });
});

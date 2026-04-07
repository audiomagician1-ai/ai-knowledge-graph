/**
 * Graph Level of Detail (LOD) — Performance optimization for large domain graphs.
 *
 * When a domain has many nodes, we can cluster by subdomain to reduce render load.
 * The 3D graph switches between:
 * - Full detail: All nodes visible (< LOD_THRESHOLD nodes)
 * - Clustered: Nodes grouped by subdomain with summary stats (>= LOD_THRESHOLD)
 *
 * This module provides the clustering logic; the actual rendering is handled by KnowledgeGraph.
 */

import type { GraphNode, GraphEdge } from '@akg/shared';

export const LOD_THRESHOLD = 200;
export const LOD_MAX_VISIBLE = 150;

export interface ClusterNode {
  id: string;
  label: string;
  subdomain: string;
  nodeCount: number;
  masteredCount: number;
  learningCount: number;
  difficulty: number;
  is_cluster: true;
  color?: string;
  /** Original node IDs in this cluster */
  children: string[];
}

export interface LODResult {
  mode: 'full' | 'clustered';
  nodes: (GraphNode | ClusterNode)[];
  edges: GraphEdge[];
  totalNodes: number;
  clusterCount?: number;
}

/**
 * Determine if LOD clustering should be applied.
 */
export function shouldCluster(nodeCount: number): boolean {
  return nodeCount >= LOD_THRESHOLD;
}

/**
 * Group nodes by subdomain and create cluster representatives.
 * Preserves important nodes (milestones, recommended, currently selected).
 */
export function clusterBySubdomain(
  nodes: GraphNode[],
  edges: GraphEdge[],
  options?: {
    preserveIds?: Set<string>; // Always show these nodes individually
    maxClusters?: number;
  }
): LODResult {
  const preserveIds = options?.preserveIds ?? new Set<string>();

  if (!shouldCluster(nodes.length)) {
    return { mode: 'full', nodes, edges, totalNodes: nodes.length };
  }

  // Group by subdomain
  const groups = new Map<string, GraphNode[]>();
  const preserved: GraphNode[] = [];

  for (const node of nodes) {
    if (preserveIds.has(node.id) || node.is_milestone || node.is_recommended) {
      preserved.push(node);
      continue;
    }

    const subdomain = node.subdomain_id || 'ungrouped';
    if (!groups.has(subdomain)) {
      groups.set(subdomain, []);
    }
    groups.get(subdomain)!.push(node);
  }

  // Create cluster nodes
  const clusters: ClusterNode[] = [];
  const nodeToCluster = new Map<string, string>();

  for (const [subdomain, groupNodes] of groups) {
    const clusterId = `cluster_${subdomain}`;
    const masteredCount = groupNodes.filter(n => n.status === 'mastered').length;
    const learningCount = groupNodes.filter(n => n.status === 'learning').length;
    const avgDifficulty = groupNodes.reduce((s, n) => s + (n.difficulty || 5), 0) / groupNodes.length;

    clusters.push({
      id: clusterId,
      label: `${subdomain} (${groupNodes.length})`,
      subdomain,
      nodeCount: groupNodes.length,
      masteredCount,
      learningCount,
      difficulty: Math.round(avgDifficulty),
      is_cluster: true,
      children: groupNodes.map(n => n.id),
    });

    for (const node of groupNodes) {
      nodeToCluster.set(node.id, clusterId);
    }
  }

  // Remap edges: merge inter-cluster edges, preserve edges to preserved nodes
  const clusterEdgeSet = new Set<string>();
  const resultEdges: GraphEdge[] = [];

  for (const edge of edges) {
    const sourceCluster = nodeToCluster.get(edge.source);
    const targetCluster = nodeToCluster.get(edge.target);

    const effectiveSource = sourceCluster || edge.source;
    const effectiveTarget = targetCluster || edge.target;

    if (effectiveSource === effectiveTarget) continue; // Skip intra-cluster edges

    const edgeKey = `${effectiveSource}->${effectiveTarget}`;
    if (clusterEdgeSet.has(edgeKey)) continue;
    clusterEdgeSet.add(edgeKey);

    resultEdges.push({
      ...edge,
      source: effectiveSource,
      target: effectiveTarget,
    });
  }

  return {
    mode: 'clustered',
    nodes: [...preserved, ...clusters],
    edges: resultEdges,
    totalNodes: nodes.length,
    clusterCount: clusters.length,
  };
}

/**
 * Calculate priority score for a node (used to decide which nodes to show in LOD).
 * Higher = more important = shown first.
 */
export function nodePriority(node: GraphNode): number {
  let score = 0;

  // Milestones are important
  if (node.is_milestone) score += 100;

  // Recommended nodes should be visible
  if (node.is_recommended) score += 80;

  // Learning nodes > not started (user is actively engaging)
  if (node.status === 'learning') score += 50;
  if (node.status === 'mastered') score += 30;

  // Higher difficulty = more notable
  score += (node.difficulty || 5) * 2;

  // High connectivity = important hub
  // (This would need edge count, approximated by whether it's an entry/exit node)

  return score;
}

/**
 * Select top-N most important nodes for display in constrained mode.
 */
export function selectTopNodes(
  nodes: GraphNode[],
  maxCount: number = LOD_MAX_VISIBLE
): GraphNode[] {
  return [...nodes]
    .sort((a, b) => nodePriority(b) - nodePriority(a))
    .slice(0, maxCount);
}

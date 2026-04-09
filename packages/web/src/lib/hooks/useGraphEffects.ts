import { useEffect } from 'react';
import type { MutableRefObject } from 'react';
import type { GraphData } from '@akg/shared';
import type { ForceGraph3DInstance } from '3d-force-graph';
import { type GNode, nodeColor, spawnCelebration } from '@/components/graph/graph-visual-utils';

/**
 * Manages KnowledgeGraph reactive effects:
 * - Node status updates + mastery celebration particles
 * - Camera fly-to on node selection
 * - Subdomain color filtering
 */
export function useGraphEffects(
  graphRef: MutableRefObject<ForceGraph3DInstance | null>,
  data: GraphData,
  selectedNodeId: string | null | undefined,
  activeSubdomain: string | null | undefined,
  prevMasteredRef: MutableRefObject<Set<string>>,
) {
  /* ── Update node visuals when data changes ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G) return;
    const prevMastered = prevMasteredRef.current;
    const currMastered = new Set<string>();
    const nodeMap = new Map(data.nodes.map(n => [n.id, n]));
    const gNodes = G.graphData().nodes as GNode[];
    for (const gn of gNodes) {
      const src = nodeMap.get(gn.id);
      if (src) { gn.status = src.status; gn.is_recommended = src.is_recommended; if (src.status === 'mastered') currMastered.add(src.id); }
    }
    G.nodeColor((n: object) => nodeColor(n as GNode));
    G.nodeThreeObject(G.nodeThreeObject());
    for (const id of currMastered) {
      if (!prevMastered.has(id)) {
        const node = gNodes.find(n => n.id === id);
        if (node && node.x != null) spawnCelebration(G.scene(), node.x!, node.y!, node.z!);
      }
    }
    prevMasteredRef.current = currMastered;
  }, [data, graphRef, prevMasteredRef]);

  /* ── Fly to selected / restore orbit ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G) return;
    if (!selectedNodeId) {
      const ctrl = G.controls() as { autoRotate?: boolean; target?: { set: (x: number, y: number, z: number) => void } };
      if (ctrl) { ctrl.autoRotate = true; if (ctrl.target) ctrl.target.set(0, 0, 0); }
      G.cameraPosition({ x: 0, y: 100, z: 700 }, { x: 0, y: 0, z: 0 }, 1000);
      return;
    }
    const nodes = G.graphData().nodes as GNode[];
    const node = nodes.find((n) => n.id === selectedNodeId);
    if (!node || node.x == null) return;
    const ctrl = G.controls() as { autoRotate?: boolean };
    if (ctrl) ctrl.autoRotate = false;
    const dist = 120;
    const nx = node.x || 0, ny = node.y || 0, nz = node.z || 0;
    const len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
    G.cameraPosition(
      { x: nx + (nx / len) * dist, y: ny + (ny / len) * dist * 0.3, z: nz + (nz / len) * dist },
      { x: nx, y: ny, z: nz }, 1000,
    );
  }, [selectedNodeId, graphRef]);

  /* ── Subdomain filter ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G) return;
    if (activeSubdomain) {
      G.nodeColor((n: object) => { const gn = n as GNode; return gn.subdomain_id === activeSubdomain ? nodeColor(gn) : '#d1d5db'; });
      G.nodeOpacity(0.4); G.linkOpacity(0.08);
    } else {
      G.nodeColor((n: object) => nodeColor(n as GNode));
      G.nodeOpacity(0.9); G.linkOpacity(0.3);
    }
    G.nodeRelSize(3);
  }, [activeSubdomain, graphRef]);
}

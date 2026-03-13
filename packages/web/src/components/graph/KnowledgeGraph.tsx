import { useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import type { GraphData, GraphNode } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';
import type { ForceGraph3DInstance } from '3d-force-graph';
// NodeObject / LinkObject re-exported from 3d-force-graph
import type { NodeObject, LinkObject } from '3d-force-graph';

/* ── Props ── */
interface KnowledgeGraphProps {
  data: GraphData;
  onNodeClick: (node: GraphNode) => void;
  selectedNodeId?: string | null;
  activeSubdomain?: string | null;
}

/* ── Extended node / link with our fields ── */
interface GNode extends NodeObject {
  id: string;
  label: string;
  subdomain_id: string;
  difficulty: number;
  status: string;
  is_milestone: boolean;
  estimated_minutes?: number;
  content_type?: string;
  // force-graph injects these:
  x?: number; y?: number; z?: number;
}

interface GLink extends LinkObject<GNode> {
  relation_type: string;
  strength: number;
}

const SUBDOMAIN_COLORS = GRAPH_VISUAL.SUBDOMAIN_COLORS;
const BG_COLOR = '#06090f';

/* ── Sphere radius for layout constraining ── */
const SPHERE_R = 280;

/* ── Node size helpers ── */
function baseSize(n: GNode): number {
  const s = 1.5 + n.difficulty * 0.45; // 1.5 – 5.55
  return n.is_milestone ? s * 1.6 : s;
}

function nodeColor(n: GNode): string {
  if (n.status === 'mastered') return '#34d399';
  if (n.status === 'learning') return '#fbbf24';
  return SUBDOMAIN_COLORS[n.subdomain_id] || '#6366f1';
}

/* ── Glow sprite texture (shared) ── */
let _glowTex: THREE.Texture | null = null;
function glowTexture(): THREE.Texture {
  if (_glowTex) return _glowTex;
  const size = 128;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(255,255,255,0.6)');
  g.addColorStop(0.3, 'rgba(255,255,255,0.15)');
  g.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, size, size);
  _glowTex = new THREE.CanvasTexture(canvas);
  return _glowTex;
}

/* ── Component ── */
export function KnowledgeGraph({ data, onNodeClick, selectedNodeId, activeSubdomain }: KnowledgeGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<ForceGraph3DInstance | null>(null);
  const hoveredRef = useRef<GNode | null>(null);

  /* Build graph data payload */
  const graphPayload = useCallback(() => {
    const nodes: GNode[] = data.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      subdomain_id: n.subdomain_id,
      difficulty: n.difficulty,
      status: n.status,
      is_milestone: n.is_milestone,
      estimated_minutes: n.estimated_minutes,
      content_type: n.content_type,
    }));
    const links: GLink[] = data.edges.map((e) => ({
      source: e.source,
      target: e.target,
      relation_type: e.relation_type,
      strength: e.strength,
    }));
    return { nodes, links };
  }, [data]);

  /* ── Init graph ── */
  useEffect(() => {
    if (!containerRef.current || !data.nodes.length) return;

    let destroyed = false;

    // Dynamic import (3d-force-graph is ESM default export)
    import('3d-force-graph').then(({ default: ForceGraph3D }) => {
      if (destroyed || !containerRef.current) return;

      const Graph = new ForceGraph3D(containerRef.current, {
        controlType: 'orbit',
      });

      /* ── Scene setup ── */
      Graph
        .backgroundColor(BG_COLOR)
        .showNavInfo(false)
        .graphData(graphPayload());

      /* ── Fog — exponential distance fade ── */
      const scene = Graph.scene();
      scene.fog = new THREE.FogExp2(BG_COLOR, 0.0018);

      /* ── Ambient + point lights ── */
      Graph.lights([
        new THREE.AmbientLight(0xffffff, 0.6),
        (() => { const l = new THREE.PointLight(0x6366f1, 1.2, 800); l.position.set(0, 0, 0); return l; })(),
        (() => { const l = new THREE.PointLight(0x8b5cf6, 0.6, 600); l.position.set(200, 200, 200); return l; })(),
      ]);

      /* ── Force: constrain to sphere surface ── */
      // @ts-ignore d3Force is dynamically available
      Graph.d3Force('radial', null); // remove default if any
      // @ts-ignore d3Force
      Graph.d3Force('charge')?.strength(-40);
      // @ts-ignore d3Force
      Graph.d3Force('link')?.distance((link: GLink) => {
        return link.relation_type === 'prerequisite' ? 50 : 70;
      });

      // Custom sphere-surface constraining force
      Graph.onEngineTick(() => {
        const nodes = Graph.graphData().nodes as GNode[];
        nodes.forEach((n) => {
          if (n.x == null || n.y == null || n.z == null) return;
          const dist = Math.sqrt(n.x * n.x + n.y * n.y + n.z * n.z) || 1;
          const scale = SPHERE_R / dist;
          // Pull gently toward sphere surface (elastic, not rigid)
          const pull = 0.03;
          n.x! += (n.x! * scale - n.x!) * pull;
          n.y! += (n.y! * scale - n.y!) * pull;
          n.z! += (n.z! * scale - n.z!) * pull;
        });
      });

      /* ── Node visuals ── */
      Graph
        .nodeVal((n: object) => baseSize(n as GNode) * baseSize(n as GNode))
        .nodeColor((n: object) => nodeColor(n as GNode))
        .nodeOpacity(0.92)
        .nodeResolution(16)
        .nodeLabel('')  // we show label via nodeThreeObjectExtend
        .nodeThreeObjectExtend(true)
        .nodeThreeObject((obj: object) => {
          const n = obj as GNode;
          const group = new THREE.Group();
          const color = nodeColor(n);

          /* Glow sprite for milestone nodes */
          if (n.is_milestone) {
            const sprite = new THREE.Sprite(
              new THREE.SpriteMaterial({
                map: glowTexture(),
                color: new THREE.Color('#fbbf24'),
                transparent: true,
                opacity: 0.55,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
              })
            );
            const s = baseSize(n) * 5;
            sprite.scale.set(s, s, 1);
            group.add(sprite);
          }

          /* Label sprite (always visible, distance-scaled) */
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d')!;
          const fontSize = n.is_milestone ? 36 : 28;
          ctx.font = `600 ${fontSize}px "DM Sans", system-ui, sans-serif`;
          const text = n.label;
          const metrics = ctx.measureText(text);
          const w = Math.ceil(metrics.width) + 12;
          const h = fontSize + 12;
          canvas.width = w; canvas.height = h;

          ctx.font = `600 ${fontSize}px "DM Sans", system-ui, sans-serif`;
          ctx.textBaseline = 'middle';
          ctx.textAlign = 'center';
          // text shadow
          ctx.fillStyle = BG_COLOR;
          ctx.globalAlpha = 0.7;
          ctx.fillText(text, w / 2 + 1, h / 2 + 1);
          ctx.globalAlpha = 1;
          ctx.fillStyle = n.is_milestone ? '#fde68a' : color;
          ctx.fillText(text, w / 2, h / 2);

          const tex = new THREE.CanvasTexture(canvas);
          tex.minFilter = THREE.LinearFilter;
          const spriteMat = new THREE.SpriteMaterial({
            map: tex,
            transparent: true,
            opacity: n.is_milestone ? 1 : 0.8,
            depthWrite: false,
          });
          const labelSprite = new THREE.Sprite(spriteMat);
          const labelScale = (n.is_milestone ? 0.35 : 0.25) * (w / h);
          const vScale = n.is_milestone ? 0.35 : 0.25;
          labelSprite.scale.set(labelScale * h * 0.12, vScale * h * 0.12, 1);
          labelSprite.position.set(0, -(baseSize(n) * 1.1 + 2), 0);
          group.add(labelSprite);

          return group;
        });

      /* ── Link visuals ── */
      Graph
        .linkWidth((l: object) => (l as GLink).relation_type === 'prerequisite' ? 0.4 : 0.15)
        .linkOpacity(0.25)
        .linkColor((l: object) => (l as GLink).relation_type === 'prerequisite' ? '#334177' : '#1a2540')
        .linkDirectionalParticles((l: object) => (l as GLink).relation_type === 'prerequisite' ? 2 : 0)
        .linkDirectionalParticleWidth(0.8)
        .linkDirectionalParticleSpeed(0.004)
        .linkDirectionalParticleColor(() => '#6366f1');

      /* ── Interaction ── */
      Graph.onNodeClick((n: NodeObject) => {
        const node = n as GNode;
        onNodeClick({
          id: node.id,
          label: node.label,
          domain_id: 'ai-engineering',
          subdomain_id: node.subdomain_id,
          difficulty: node.difficulty,
          status: node.status,
          is_milestone: node.is_milestone,
          estimated_minutes: node.estimated_minutes,
          content_type: node.content_type,
        } as GraphNode);

        // Fly camera to the clicked node
        const dist = 100;
        const pos = { x: (node.x || 0) + dist, y: (node.y || 0) + dist * 0.3, z: (node.z || 0) + dist };
        Graph.cameraPosition(pos, { x: node.x || 0, y: node.y || 0, z: node.z || 0 }, 800);
      });

      Graph.onNodeHover((n: NodeObject | null) => {
        hoveredRef.current = n as GNode | null;
        containerRef.current!.style.cursor = n ? 'pointer' : 'default';
      });

      Graph.onBackgroundClick(() => {
        onNodeClick(null as unknown as GraphNode);
      });

      /* ── Auto-rotate ── */
      const ctrl = Graph.controls() as { autoRotate?: boolean; autoRotateSpeed?: number; enableDamping?: boolean };
      if (ctrl) {
        ctrl.autoRotate = true;
        ctrl.autoRotateSpeed = 0.4;
        ctrl.enableDamping = true;
      }

      /* ── Camera start position ── */
      Graph.cameraPosition({ x: 0, y: 80, z: 450 });

      /* ── Resize handling ── */
      const ro = new ResizeObserver((entries) => {
        for (const e of entries) {
          const { width, height } = e.contentRect;
          if (width && height) Graph.width(width).height(height);
        }
      });
      ro.observe(containerRef.current);

      graphRef.current = Graph;

      return () => {
        destroyed = true;
        ro.disconnect();
        Graph._destructor();
        graphRef.current = null;
      };
    });

    // cleanup in case the promise never resolves
    return () => { destroyed = true; };
  }, [data, graphPayload, onNodeClick]);

  /* ── Fly to selected node from outside ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G || !selectedNodeId) return;
    const nodes = G.graphData().nodes as GNode[];
    const node = nodes.find((n) => n.id === selectedNodeId);
    if (!node || node.x == null) return;
    const dist = 100;
    G.cameraPosition(
      { x: (node.x || 0) + dist, y: (node.y || 0) + dist * 0.3, z: (node.z || 0) + dist },
      { x: node.x || 0, y: node.y || 0, z: node.z || 0 },
      800,
    );
  }, [selectedNodeId]);

  /* ── Subdomain filter: change node opacity ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G) return;
    G.nodeOpacity(0.92); // reset
    if (activeSubdomain) {
      G.nodeThreeObjectExtend(true);
      G.nodeColor((n: object) => {
        const gn = n as GNode;
        if (gn.subdomain_id === activeSubdomain) return nodeColor(gn);
        return '#1a2540';
      });
      G.nodeOpacity(0.5);
      G.linkOpacity(0.08);
    } else {
      G.nodeColor((n: object) => nodeColor(n as GNode));
      G.nodeOpacity(0.92);
      G.linkOpacity(0.25);
    }
    // Refresh rendering
    G.nodeRelSize(4);
  }, [activeSubdomain]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full graph-container"
      style={{ backgroundColor: BG_COLOR }}
    />
  );
}
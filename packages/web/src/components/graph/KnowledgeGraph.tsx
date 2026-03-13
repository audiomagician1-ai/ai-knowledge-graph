import { useEffect, useRef, useCallback } from 'react';
import * as THREE from 'three';
import type { GraphData, GraphNode } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';
import type { ForceGraph3DInstance } from '3d-force-graph';
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
  x?: number; y?: number; z?: number;
}

interface GLink extends LinkObject<GNode> {
  relation_type: string;
  strength: number;
}

const SUBDOMAIN_COLORS = GRAPH_VISUAL.SUBDOMAIN_COLORS;
const BG_COLOR = '#06090f';

/* ── Larger sphere to spread 267 nodes ── */
const SPHERE_R = 480;

/* ── Node size: MUCH smaller than before ── */
function baseSize(n: GNode): number {
  // Tiny dots: 0.6 – 1.8 base (was 1.5 – 5.55!)
  const s = 0.6 + n.difficulty * 0.13;
  return n.is_milestone ? s * 1.5 : s;
}

function nodeColor(n: GNode): string {
  if (n.status === 'mastered') return '#34d399';
  if (n.status === 'learning') return '#fbbf24';
  return SUBDOMAIN_COLORS[n.subdomain_id] || '#6366f1';
}

/* ── Label texture cache to avoid re-creating every frame ── */
const _labelCache = new Map<string, THREE.Texture>();

function makeLabelTexture(text: string, color: string, isMilestone: boolean): THREE.Texture {
  const key = `${text}|${color}|${isMilestone}`;
  if (_labelCache.has(key)) return _labelCache.get(key)!;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d')!;
  // Use large font for crisp rendering on canvas, then scale sprite down
  const fontSize = isMilestone ? 72 : 56;
  const fontFamily = '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", system-ui, sans-serif';
  ctx.font = `700 ${fontSize}px ${fontFamily}`;
  const metrics = ctx.measureText(text);
  const pad = 24;
  const w = Math.ceil(metrics.width) + pad * 2;
  const h = fontSize + pad;
  canvas.width = w;
  canvas.height = h;

  // Re-set font after resize
  ctx.font = `700 ${fontSize}px ${fontFamily}`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  // Dark outline/shadow for readability
  ctx.strokeStyle = 'rgba(6, 9, 15, 0.95)';
  ctx.lineWidth = 6;
  ctx.lineJoin = 'round';
  ctx.strokeText(text, w / 2, h / 2);

  // Fill text
  ctx.fillStyle = isMilestone ? '#fde68a' : color;
  ctx.fillText(text, w / 2, h / 2);

  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  tex.magFilter = THREE.LinearFilter;
  _labelCache.set(key, tex);
  return tex;
}

/* ── Glow sprite texture (shared) ── */
let _glowTex: THREE.Texture | null = null;
function glowTexture(): THREE.Texture {
  if (_glowTex) return _glowTex;
  const size = 256;
  const canvas = document.createElement('canvas');
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext('2d')!;
  const g = ctx.createRadialGradient(size / 2, size / 2, 0, size / 2, size / 2, size / 2);
  g.addColorStop(0, 'rgba(251,191,36,0.5)');
  g.addColorStop(0.25, 'rgba(251,191,36,0.15)');
  g.addColorStop(0.6, 'rgba(251,191,36,0.03)');
  g.addColorStop(1, 'rgba(0,0,0,0)');
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

      /* ── Much lighter fog so labels stay visible ── */
      const scene = Graph.scene();
      scene.fog = new THREE.FogExp2(BG_COLOR, 0.0006);

      /* ── Brighter lights ── */
      Graph.lights([
        new THREE.AmbientLight(0xffffff, 0.9),
        (() => { const l = new THREE.PointLight(0x6366f1, 0.8, 1200); l.position.set(0, 0, 0); return l; })(),
        (() => { const l = new THREE.PointLight(0x8b5cf6, 0.4, 800); l.position.set(300, 300, 300); return l; })(),
      ]);

      /* ── Forces: stronger repulsion to prevent overlap ── */
      // @ts-ignore d3Force
      Graph.d3Force('radial', null);
      // @ts-ignore d3Force — much stronger repulsion (was -40)
      Graph.d3Force('charge')?.strength(-120);
      // @ts-ignore d3Force — longer link distances
      Graph.d3Force('link')?.distance((link: GLink) => {
        return link.relation_type === 'prerequisite' ? 80 : 110;
      });

      // Sphere-surface constraining force
      Graph.onEngineTick(() => {
        const nodes = Graph.graphData().nodes as GNode[];
        nodes.forEach((n) => {
          if (n.x == null || n.y == null || n.z == null) return;
          const dist = Math.sqrt(n.x * n.x + n.y * n.y + n.z * n.z) || 1;
          const scale = SPHERE_R / dist;
          const pull = 0.02;
          n.x! += (n.x! * scale - n.x!) * pull;
          n.y! += (n.y! * scale - n.y!) * pull;
          n.z! += (n.z! * scale - n.z!) * pull;
        });
      });

      /* ── Node visuals: small spheres ── */
      Graph
        .nodeVal((n: object) => {
          const s = baseSize(n as GNode);
          return s * s;
        })
        .nodeColor((n: object) => nodeColor(n as GNode))
        .nodeOpacity(0.85)
        .nodeResolution(12)
        .nodeRelSize(3) // smaller base multiplier (was default 4)
        .nodeLabel('') // labels via sprites
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
                transparent: true,
                opacity: 0.6,
                depthWrite: false,
                blending: THREE.AdditiveBlending,
              })
            );
            const s = baseSize(n) * 12;
            sprite.scale.set(s, s, 1);
            group.add(sprite);
          }

          /* Label sprite — large, crisp, always visible */
          const tex = makeLabelTexture(n.label, color, n.is_milestone);
          const spriteMat = new THREE.SpriteMaterial({
            map: tex,
            transparent: true,
            opacity: n.is_milestone ? 1.0 : 0.9,
            depthWrite: false,
            sizeAttenuation: true,
          });
          const labelSprite = new THREE.Sprite(spriteMat);
          // Scale: each canvas pixel ≈ 0.14 world units
          const img = tex.image as { width: number; height: number };
          const aspect = img.width / img.height;
          const labelH = n.is_milestone ? 8 : 6;
          labelSprite.scale.set(labelH * aspect, labelH, 1);
          // Position below the node sphere
          labelSprite.position.set(0, -(baseSize(n) * 2.5 + 3), 0);
          group.add(labelSprite);

          return group;
        });

      /* ── Link visuals: thicker, more visible ── */
      Graph
        .linkWidth((l: object) => (l as GLink).relation_type === 'prerequisite' ? 1.0 : 0.5)
        .linkOpacity(0.35)
        .linkColor((l: object) => (l as GLink).relation_type === 'prerequisite' ? '#4a5880' : '#2a3654')
        .linkDirectionalParticles((l: object) => (l as GLink).relation_type === 'prerequisite' ? 2 : 0)
        .linkDirectionalParticleWidth(1.2)
        .linkDirectionalParticleSpeed(0.003)
        .linkDirectionalParticleColor(() => '#818cf8');

      /* ── Interaction: STOP rotation on click + camera fly ── */
      Graph.onNodeClick((n: NodeObject) => {
        const node = n as GNode;

        // Stop auto-rotation
        const ctrl = Graph.controls() as { autoRotate?: boolean };
        if (ctrl) ctrl.autoRotate = false;

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

        // Smooth camera fly to node
        const dist = 120;
        const nx = node.x || 0, ny = node.y || 0, nz = node.z || 0;
        const len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
        // Position camera along the node's radial direction (outside the sphere looking in)
        const camX = nx + (nx / len) * dist;
        const camY = ny + (ny / len) * dist * 0.3;
        const camZ = nz + (nz / len) * dist;
        Graph.cameraPosition(
          { x: camX, y: camY, z: camZ },
          { x: nx, y: ny, z: nz },
          1000,
        );
      });

      Graph.onNodeHover((n: NodeObject | null) => {
        hoveredRef.current = n as GNode | null;
        if (containerRef.current) {
          containerRef.current.style.cursor = n ? 'pointer' : 'default';
        }
      });

      Graph.onBackgroundClick(() => {
        // Resume auto-rotation on background click
        const ctrl = Graph.controls() as { autoRotate?: boolean };
        if (ctrl) ctrl.autoRotate = true;
        onNodeClick(null as unknown as GraphNode);
      });

      /* ── Auto-rotate (slow) ── */
      const ctrl = Graph.controls() as { autoRotate?: boolean; autoRotateSpeed?: number; enableDamping?: boolean; dampingFactor?: number };
      if (ctrl) {
        ctrl.autoRotate = true;
        ctrl.autoRotateSpeed = 0.3;
        ctrl.enableDamping = true;
        ctrl.dampingFactor = 0.12;
      }

      /* ── Camera start: further out so we see the whole sphere ── */
      Graph.cameraPosition({ x: 0, y: 100, z: 700 });

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

    return () => { destroyed = true; };
  }, [data, graphPayload, onNodeClick]);

  /* ── Fly to selected node from outside ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G || !selectedNodeId) return;
    const nodes = G.graphData().nodes as GNode[];
    const node = nodes.find((n) => n.id === selectedNodeId);
    if (!node || node.x == null) return;

    // Stop rotation when selecting
    const ctrl = G.controls() as { autoRotate?: boolean };
    if (ctrl) ctrl.autoRotate = false;

    const dist = 120;
    const nx = node.x || 0, ny = node.y || 0, nz = node.z || 0;
    const len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
    G.cameraPosition(
      { x: nx + (nx / len) * dist, y: ny + (ny / len) * dist * 0.3, z: nz + (nz / len) * dist },
      { x: nx, y: ny, z: nz },
      1000,
    );
  }, [selectedNodeId]);

  /* ── Subdomain filter ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G) return;
    if (activeSubdomain) {
      G.nodeColor((n: object) => {
        const gn = n as GNode;
        return gn.subdomain_id === activeSubdomain ? nodeColor(gn) : '#1a2540';
      });
      G.nodeOpacity(0.4);
      G.linkOpacity(0.06);
    } else {
      G.nodeColor((n: object) => nodeColor(n as GNode));
      G.nodeOpacity(0.85);
      G.linkOpacity(0.35);
    }
    G.nodeRelSize(3);
  }, [activeSubdomain]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full graph-container"
      style={{ backgroundColor: BG_COLOR }}
    />
  );
}
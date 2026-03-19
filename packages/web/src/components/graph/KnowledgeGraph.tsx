import { useEffect, useRef } from 'react';
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
  /** Domain accent color from domains.json (hex). Defaults to '#8b5cf6' (violet). */
  domainColor?: string;
  /** Active domain ID, forwarded into GraphNode on click. */
  domainId?: string;
}

/* ── Extended node / link with our fields ── */
interface GNode extends NodeObject {
  id: string;
  label: string;
  domain_id: string;
  subdomain_id: string;
  difficulty: number;
  status: string;
  is_milestone: boolean;
  is_recommended?: boolean;
  estimated_minutes?: number;
  content_type?: string;
  x?: number; y?: number; z?: number;
}

interface GLink extends LinkObject<GNode> {
  relation_type: string;
  strength: number;
}

const SUBDOMAIN_COLORS = GRAPH_VISUAL.SUBDOMAIN_COLORS;
const BG_COLOR = '#e8e8e4';

/* ── Sphere layout ── */
const SPHERE_R = 480;

/* ── Node size: MUCH smaller than before ── */
function baseSize(n: GNode): number {
  // Tiny dots: 0.6 – 1.8 base (was 1.5 – 5.55!)
  const s = 0.6 + n.difficulty * 0.13;
  return n.is_milestone ? s * 1.5 : s;
}

function nodeColor(n: GNode): string {
  if (n.status === 'mastered') return '#10b981';  // emerald
  if (n.status === 'learning') return '#f59e0b';  // amber
  if (n.is_recommended) return '#06b6d4';          // cyan
  return SUBDOMAIN_COLORS[n.subdomain_id] || '#94a3b8';
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

  // Dark outline/shadow for readability — warm dark
  ctx.strokeStyle = 'rgba(242, 241, 239, 0.9)';
  ctx.lineWidth = 5;
  ctx.lineJoin = 'round';
  ctx.strokeText(text, w / 2, h / 2);

  // Fill text
      ctx.fillStyle = isMilestone ? '#b45309' : color;  // deep amber for milestones on light bg
  ctx.fillText(text, w / 2, h / 2);

  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  tex.magFilter = THREE.LinearFilter;
  _labelCache.set(key, tex);
  return tex;
}

/* (glow textures removed — Observatory Study: no glow) */

/* ── Celebration particles for newly mastered nodes ── */
function spawnCelebration(scene: THREE.Scene, x: number, y: number, z: number) {
  const PARTICLE_COUNT = 24;
  const colors = [0x10b981, 0xf59e0b, 0x06b6d4, 0x6366f1, 0xec4899]; // emerald, amber, cyan, indigo, pink

  const particles: { mesh: THREE.Mesh; vx: number; vy: number; vz: number; life: number }[] = [];

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const color = colors[i % colors.length];
    const geo = new THREE.SphereGeometry(0.6 + Math.random() * 0.8, 6, 6);
    const mat = new THREE.MeshBasicMaterial({
      color,
      transparent: true,
      opacity: 1,
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, y, z);

    // Random velocity in all directions
    const speed = 1.5 + Math.random() * 3;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.random() * Math.PI;
    const vx = speed * Math.sin(phi) * Math.cos(theta);
    const vy = speed * Math.sin(phi) * Math.sin(theta);
    const vz = speed * Math.cos(phi);

    scene.add(mesh);
    particles.push({ mesh, vx, vy, vz, life: 1.0 });
  }

  // Animate particles
  let frame = 0;
  const maxFrames = 60; // ~1 second at 60fps
  const animate = () => {
    frame++;
    if (frame > maxFrames) {
      // Cleanup
      for (const p of particles) {
        scene.remove(p.mesh);
        p.mesh.geometry.dispose();
        (p.mesh.material as THREE.MeshBasicMaterial).dispose();
      }
      return;
    }
    for (const p of particles) {
      p.mesh.position.x += p.vx;
      p.mesh.position.y += p.vy;
      p.mesh.position.z += p.vz;
      p.life -= 1 / maxFrames;
      (p.mesh.material as THREE.MeshBasicMaterial).opacity = Math.max(0, p.life);
      p.vx *= 0.96; p.vy *= 0.96; p.vz *= 0.96; // friction
    }
    requestAnimationFrame(animate);
  };
  requestAnimationFrame(animate);
}

/* ── Component ── */
const DEFAULT_DOMAIN_COLOR = '#8b5cf6'; // violet
const DEFAULT_DOMAIN_ID = 'ai-engineering';

export function KnowledgeGraph({ data, onNodeClick, selectedNodeId, activeSubdomain, domainColor, domainId }: KnowledgeGraphProps) {
  const effectiveDomainColor = domainColor || DEFAULT_DOMAIN_COLOR;
  const effectiveDomainId = domainId || DEFAULT_DOMAIN_ID;
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<ForceGraph3DInstance | null>(null);
  const hoveredRef = useRef<GNode | null>(null);
  const prevMasteredRef = useRef<Set<string>>(new Set(
    data.nodes.filter(n => n.status === 'mastered').map(n => n.id)
  ));
  // Use refs for callbacks to avoid re-init on every render
  const onNodeClickRef = useRef(onNodeClick);
  onNodeClickRef.current = onNodeClick;
  const dataRef = useRef(data);
  dataRef.current = data;

  // Store refs for domain props so they're available in callbacks without re-init
  const domainColorRef = useRef(effectiveDomainColor);
  domainColorRef.current = effectiveDomainColor;
  const domainIdRef = useRef(effectiveDomainId);
  domainIdRef.current = effectiveDomainId;

  /* Build graph data payload from ref (stable) */
  const buildPayload = () => {
    const d = dataRef.current;
    const nodes: GNode[] = d.nodes.map((n) => ({
      id: n.id,
      label: n.label,
      domain_id: n.domain_id,
      subdomain_id: n.subdomain_id,
      difficulty: n.difficulty,
      status: n.status,
      is_milestone: n.is_milestone,
      is_recommended: n.is_recommended,
      estimated_minutes: n.estimated_minutes,
      content_type: n.content_type,
    }));
    const links: GLink[] = d.edges.map((e) => ({
      source: e.source,
      target: e.target,
      relation_type: e.relation_type,
      strength: e.strength,
    }));
    return { nodes, links };
  };

  /* ── Init graph — runs ONCE, not on every data/callback change ── */
  useEffect(() => {
    if (!containerRef.current || !dataRef.current.nodes.length) return;

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
        .graphData(buildPayload());

      /* ── Subtle fog ── */
      const scene = Graph.scene();
      scene.fog = new THREE.FogExp2(0xe8e8e4, 0.0003);

      /* ── Bright neutral lights + domain-tinted accent light ── */
      const domainThreeColor = new THREE.Color(domainColorRef.current);
      Graph.lights([
        new THREE.AmbientLight(0xffffff, 1.1),
        (() => { const l = new THREE.PointLight(0xffffff, 0.3, 1200); l.position.set(200, 300, 200); return l; })(),
        (() => { const l = new THREE.PointLight(domainThreeColor, 0.25, 1400); l.position.set(-300, -100, 300); return l; })(),
      ]);

      /* ── Forces ── */
      // @ts-ignore d3Force
      Graph.d3Force('radial', null);
      // @ts-ignore d3Force
      Graph.d3Force('charge')?.strength(-120);
      // @ts-ignore d3Force
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

          /* No glow sprites — clean solid nodes */

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

      /* ── Link visuals: visible, fresh lines ── */
      Graph
        .linkWidth((l: object) => (l as GLink).relation_type === 'prerequisite' ? 1.2 : 0.6)
        .linkOpacity(0.3)
        .linkColor((l: object) => {
          const link = l as GLink;
          return link.relation_type === 'prerequisite' ? '#94a3b8' : '#cbd5e1';
        })
        .linkDirectionalParticles((l: object) => (l as GLink).relation_type === 'prerequisite' ? 2 : 0)
        .linkDirectionalParticleWidth(1.5)
        .linkDirectionalParticleSpeed(0.004)
        .linkDirectionalParticleColor(() => domainColorRef.current);

      /* ── Interaction: STOP rotation + FREEZE simulation on click ── */
      Graph.onNodeClick((n: NodeObject) => {
        const node = n as GNode;

        // 1) Stop auto-rotation
        const ctrl = Graph.controls() as { autoRotate?: boolean };
        if (ctrl) ctrl.autoRotate = false;

        // 2) Freeze the physics simulation so nodes don't scramble
        Graph.cooldownTime(0);        // stop simulation immediately
        // Don't reheat — simulation is frozen

        // 3) Notify parent via ref (avoids re-init)
        onNodeClickRef.current({
          id: node.id,
          label: node.label,
          domain_id: node.domain_id || domainIdRef.current,
          subdomain_id: node.subdomain_id,
          difficulty: node.difficulty,
          status: node.status,
          is_milestone: node.is_milestone,
          is_recommended: node.is_recommended,
          estimated_minutes: node.estimated_minutes,
          content_type: node.content_type,
        } as GraphNode);

        // 4) Smooth camera fly to node
        const dist = 140;
        const nx = node.x || 0, ny = node.y || 0, nz = node.z || 0;
        const len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
        Graph.cameraPosition(
          { x: nx + (nx / len) * dist, y: ny + (ny / len) * dist * 0.3, z: nz + (nz / len) * dist },
          { x: nx, y: ny, z: nz },
          1200,
        );
      });

      Graph.onNodeHover((n: NodeObject | null) => {
        hoveredRef.current = n as GNode | null;
        if (containerRef.current) {
          containerRef.current.style.cursor = n ? 'pointer' : 'default';
        }
      });

      Graph.onBackgroundClick(() => {
        const ctrl = Graph.controls() as { autoRotate?: boolean; target?: { set: (x: number, y: number, z: number) => void } };
        if (ctrl) {
          ctrl.autoRotate = true;
          // Reset orbit target to sphere center
          if (ctrl.target) ctrl.target.set(0, 0, 0);
        }
        onNodeClickRef.current(null as unknown as GraphNode);
      });

      /* ── Auto-rotate (slow) ── */
      const ctrl = Graph.controls() as { autoRotate?: boolean; autoRotateSpeed?: number; enableDamping?: boolean; dampingFactor?: number };
      if (ctrl) {
        ctrl.autoRotate = true;
        ctrl.autoRotateSpeed = 0.15;
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

    return () => {
      destroyed = true;
      // Cleanup graph instance stored in ref (the .then() cleanup won't run as useEffect cleanup)
      if (graphRef.current) {
        graphRef.current._destructor();
        graphRef.current = null;
      }
      // Dispose all cached label textures to free GPU memory
      for (const tex of _labelCache.values()) tex.dispose();
      _labelCache.clear();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Init ONCE — data changes handled via separate effect

  /* ── Update node visuals when data (status) changes ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G) return;

    // Collect IDs of previously-mastered nodes
    const prevMastered = prevMasteredRef.current;
    const currMastered = new Set<string>();

    // Build lookup map for O(1) matching (avoid O(N²))
    const nodeMap = new Map(data.nodes.map(n => [n.id, n]));

    // Update graphData node properties in-place
    const gNodes = G.graphData().nodes as GNode[];
    for (const gn of gNodes) {
      const src = nodeMap.get(gn.id);
      if (src) {
        gn.status = src.status;
        gn.is_recommended = src.is_recommended;
        if (src.status === 'mastered') currMastered.add(src.id);
      }
    }

    // Trigger visual refresh: nodeColor + regenerate three objects (for glow changes)
    G.nodeColor((n: object) => nodeColor(n as GNode));
    // Force nodeThreeObject rebuild by re-setting the same function
    G.nodeThreeObject(G.nodeThreeObject());

    // Detect newly mastered nodes → fire celebration particles
    for (const id of currMastered) {
      if (!prevMastered.has(id)) {
        const node = gNodes.find(n => n.id === id);
        if (node && node.x != null) {
          spawnCelebration(G.scene(), node.x!, node.y!, node.z!);
        }
      }
    }
    prevMasteredRef.current = currMastered;
  }, [data]);

  /* ── Fly to selected node / restore free orbit when deselected ── */
  useEffect(() => {
    const G = graphRef.current;
    if (!G) return;

    if (!selectedNodeId) {
      // Panel closed → restore free orbit rotation + reset lookAt to sphere center
      const ctrl = G.controls() as { autoRotate?: boolean; target?: { set: (x: number, y: number, z: number) => void } };
      if (ctrl) {
        ctrl.autoRotate = true;
        // Reset orbit target to sphere center so camera orbits the whole globe
        if (ctrl.target) ctrl.target.set(0, 0, 0);
      }
      // Smoothly fly camera back to overview position
      G.cameraPosition(
        { x: 0, y: 100, z: 700 },  // same as initial position
        { x: 0, y: 0, z: 0 },       // look at center
        1000,
      );
      return;
    }

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
        return gn.subdomain_id === activeSubdomain ? nodeColor(gn) : '#d1d5db';
      });
      G.nodeOpacity(0.4);
      G.linkOpacity(0.08);
    } else {
      G.nodeColor((n: object) => nodeColor(n as GNode));
      G.nodeOpacity(0.9);
      G.linkOpacity(0.3);
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
import { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { peekDomainProgress } from '@/lib/store/learning';
import { fetchDomainLinks, type DomainLink } from '@/lib/api/graph-api';
import { Loader } from 'lucide-react';
import * as THREE from 'three';
import type { ForceGraph3DInstance } from '3d-force-graph';
import type { NodeObject, LinkObject } from '3d-force-graph';

/* ─── Demo domains (fallback when backend unavailable) ─── */
const DEMO_DOMAINS: import('@akg/shared').Domain[] = [
  { id: 'ai-engineering', name: 'AI编程', description: 'AI编程知识领域', color: '#8b5cf6', is_active: true, stats: { total_concepts: 400, total_edges: 615, subdomains: 15 } },
  { id: 'mathematics', name: '数学', description: '数学知识领域', color: '#3b82f6', is_active: true, stats: { total_concepts: 269, total_edges: 366, subdomains: 12 } },
  { id: 'game-engine', name: '游戏引擎', description: '游戏引擎知识领域', color: '#059669', is_active: true, stats: { total_concepts: 300, total_edges: 319, subdomains: 15 } },
  { id: 'game-design', name: '游戏设计', description: '游戏设计知识领域', color: '#dc2626', is_active: true, stats: { total_concepts: 250, total_edges: 274, subdomains: 12 } },
  { id: 'psychology', name: '心理学', description: '心理学知识领域', color: '#a855f7', is_active: true, stats: { total_concepts: 183, total_edges: 203, subdomains: 8 } },
  { id: 'physics', name: '物理', description: '物理知识领域', color: '#22c55e', is_active: true, stats: { total_concepts: 194, total_edges: 232, subdomains: 10 } },
  { id: 'english', name: '英语', description: '英语知识领域', color: '#eab308', is_active: true, stats: { total_concepts: 200, total_edges: 229, subdomains: 10 } },
];

/* ─── Rename map: backend name → display name ─── */
const DISPLAY_NAME_OVERRIDES: Record<string, string> = {
  'ai-engineering': 'AI编程',
};

/* ─── Constants ─── */
const BG_COLOR = '#e8e8e4';
const SPHERE_R = 420;
const TRANSITION_MS = 900;
const LINK_MIN_COUNT = 5; // Only show links with >= 5 cross-domain relations (remove clutter)

/* ─── Types ─── */
interface DomainProgress { mastered: number; learning: number; total: number }

interface DNode extends NodeObject {
  id: string; name: string; color: string;
  conceptCount: number; edgeCount: number; subdomainCount: number;
  completeness: number; // composite quality score
  progress: DomainProgress;
  x?: number; y?: number; z?: number;
}

interface DLink extends LinkObject<DNode> { count: number }

/* ─── Completeness score — higher = more content-rich ─── */
function calcCompleteness(concepts: number, edges: number, subdomains: number): number {
  // Weighted: concepts (1x) + edges (0.5x) + subdomains (5x)
  return concepts + edges * 0.5 + subdomains * 5;
}

/* ─── Node visual radius based on completeness (quality → bigger sphere) ─── */
function nodeRadius(n: DNode): number {
  // Map completeness to radius range 6–18
  // Min completeness ~350 (small domains), max ~700 (AI编程)
  const minC = 300, maxC = 750;
  const minR = 6, maxR = 18;
  const t = Math.max(0, Math.min(1, (n.completeness - minC) / (maxC - minC)));
  return minR + t * (maxR - minR);
}

/* ─── Label texture cache ─── */
const _labelCache = new Map<string, THREE.Texture>();

function makeLabelTexture(name: string, stats: string): THREE.Texture {
  const key = `${name}|${stats}`;
  if (_labelCache.has(key)) return _labelCache.get(key)!;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d')!;
  const fontFamily = '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", system-ui, sans-serif';

  // 2x larger than before (was 56/28 → now 112/48)
  const nameFontSize = 112;
  const statsFontSize = 48;
  ctx.font = `700 ${nameFontSize}px ${fontFamily}`;
  const nameW = ctx.measureText(name).width;
  ctx.font = `400 ${statsFontSize}px ${fontFamily}`;
  const statsW = ctx.measureText(stats).width;

  const pad = 40;
  const w = Math.ceil(Math.max(nameW, statsW)) + pad * 2;
  const h = nameFontSize + statsFontSize + 24 + pad;
  canvas.width = w;
  canvas.height = h;

  // Name
  ctx.font = `700 ${nameFontSize}px ${fontFamily}`;
  ctx.textBaseline = 'top';
  ctx.textAlign = 'center';
  ctx.strokeStyle = 'rgba(242, 241, 239, 0.92)';
  ctx.lineWidth = 8;
  ctx.lineJoin = 'round';
  ctx.strokeText(name, w / 2, pad / 2);
  ctx.fillStyle = '#1a1a1a';
  ctx.fillText(name, w / 2, pad / 2);

  // Stats
  if (stats) {
    ctx.font = `400 ${statsFontSize}px ${fontFamily}`;
    ctx.strokeStyle = 'rgba(242, 241, 239, 0.85)';
    ctx.lineWidth = 5;
    ctx.strokeText(stats, w / 2, pad / 2 + nameFontSize + 10);
    ctx.fillStyle = '#666';
    ctx.fillText(stats, w / 2, pad / 2 + nameFontSize + 10);
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  tex.magFilter = THREE.LinearFilter;
  _labelCache.set(key, tex);
  return tex;
}

/* ═══════════════════════════════════════════
   HomePage — 3D Sphere layout
   ═══════════════════════════════════════════ */
export function HomePage() {
  const navigate = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const activeDomains = domains.filter((d) => d.is_active !== false);

  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<ForceGraph3DInstance | null>(null);
  const [domainLinks, setDomainLinks] = useState<DomainLink[]>([]);
  const [transitioning, setTransitioning] = useState<{ domainId: string; cx: number; cy: number; color: string } | null>(null);
  const transitionTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);
  const navigateRef = useRef(navigate);
  navigateRef.current = navigate;

  // Fetch data
  useEffect(() => {
    fetchDomains().then(() => {
      const state = useDomainStore.getState();
      if (state.domains.length === 0) {
        useDomainStore.setState({ domains: DEMO_DOMAINS, loading: false, error: null });
      }
    });
    fetchDomainLinks().then(setDomainLinks).catch(() => {});
  }, [fetchDomains]);

  // Cleanup
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (transitionTimerRef.current) clearTimeout(transitionTimerRef.current);
    };
  }, []);

  // Build graph data — completeness-sorted, filtered links
  const graphData = useMemo(() => {
    if (activeDomains.length === 0) return null;

    const nodes: DNode[] = activeDomains.map((d) => {
      const progress = peekDomainProgress(d.id);
      const concepts = d.stats?.total_concepts ?? 0;
      const edges = d.stats?.total_edges ?? 0;
      const subs = d.stats?.subdomains ?? 0;
      if (concepts && progress.total !== concepts) progress.total = concepts;

      const displayName = DISPLAY_NAME_OVERRIDES[d.id] || d.name;

      return {
        id: d.id,
        name: displayName,
        color: d.color,
        conceptCount: concepts,
        edgeCount: edges,
        subdomainCount: subs,
        completeness: calcCompleteness(concepts, edges, subs),
        progress,
      };
    });

    // Sort by completeness — highest first (used for camera targeting)
    nodes.sort((a, b) => b.completeness - a.completeness);

    const nodeIds = new Set(nodes.map(n => n.id));
    // Only keep strong links (count >= LINK_MIN_COUNT) to reduce visual clutter
    const links: DLink[] = domainLinks
      .filter(l => nodeIds.has(l.source) && nodeIds.has(l.target) && l.count >= LINK_MIN_COUNT)
      .map(l => ({ source: l.source, target: l.target, count: l.count }));

    return { nodes, links };
  }, [activeDomains, domainLinks]);

  // Track the most-complete domain id for camera targeting
  const topDomainId = graphData?.nodes[0]?.id;

  // Init 3D graph
  useEffect(() => {
    if (!containerRef.current || !graphData) return;

    let destroyed = false;

    import('3d-force-graph').then(({ default: ForceGraph3D }) => {
      if (destroyed || !containerRef.current) return;

      const Graph = new ForceGraph3D(containerRef.current, { controlType: 'orbit' });

      /* ── Scene ── */
      Graph.backgroundColor(BG_COLOR).showNavInfo(false).graphData(graphData as any);

      /* ── Fog ── */
      const scene = Graph.scene();
      scene.fog = new THREE.FogExp2(0xe8e8e4, 0.00012);

      /* ── Lights ── */
      Graph.lights([
        new THREE.AmbientLight(0xffffff, 1.2),
        (() => { const l = new THREE.PointLight(0xffffff, 0.4, 1500); l.position.set(300, 400, 300); return l; })(),
        (() => { const l = new THREE.PointLight(0x8b5cf6, 0.2, 1600); l.position.set(-400, -150, 400); return l; })(),
      ]);

      /* ── Forces ── */
      // @ts-ignore
      Graph.d3Force('charge')?.strength(-800);
      // @ts-ignore
      Graph.d3Force('link')?.distance((link: DLink) => {
        const count = link.count || 1;
        return Math.max(100, 200 - count * 5);
      }).strength(0.04);

      // Sphere-surface constraining force
      Graph.onEngineTick(() => {
        const nodes = Graph.graphData().nodes as DNode[];
        for (const n of nodes) {
          if (n.x == null || n.y == null || n.z == null) continue;
          const dist = Math.sqrt(n.x * n.x + n.y * n.y + n.z * n.z) || 1;
          const scale = SPHERE_R / dist;
          const pull = 0.06;
          n.x! += (n.x! * scale - n.x!) * pull;
          n.y! += (n.y! * scale - n.y!) * pull;
          n.z! += (n.z! * scale - n.z!) * pull;
        }
      });

      /* ── Node visuals ── */
      Graph
        .nodeVal((obj: object) => {
          const r = nodeRadius(obj as DNode);
          return r * r; // nodeVal is area-based
        })
        .nodeColor((obj: object) => (obj as DNode).color)
        .nodeOpacity(0.85)
        .nodeResolution(24)
        .nodeRelSize(3)
        .nodeLabel('')
        .nodeThreeObjectExtend(true)
        .nodeThreeObject((obj: object) => {
          const n = obj as DNode;
          const group = new THREE.Group();

          // Label sprite — centered on the sphere (position 0,0,0)
          const stats: string[] = [];
          if (n.conceptCount) stats.push(`${n.conceptCount} 知识点`);
          if (n.subdomainCount) stats.push(`${n.subdomainCount} 子领域`);
          const tex = makeLabelTexture(n.name, stats.join(' · '));
          const spriteMat = new THREE.SpriteMaterial({
            map: tex, transparent: true, opacity: 0.95,
            depthWrite: false, sizeAttenuation: true,
          });
          const sprite = new THREE.Sprite(spriteMat);
          const img = tex.image as { width: number; height: number };
          const aspect = img.width / img.height;
          const labelH = 16; // 2x from before (was 8)
          sprite.scale.set(labelH * aspect, labelH, 1);
          sprite.position.set(0, 0, 0); // centered on sphere
          sprite.renderOrder = 1; // render on top of sphere
          group.add(sprite);

          return group;
        });

      /* ── Link visuals — only strong connections shown ── */
      Graph
        .linkWidth((obj: object) => {
          const l = obj as DLink;
          return Math.min(2, 0.3 + (l.count || 1) * 0.1);
        })
        .linkOpacity(0.18)
        .linkColor(() => '#94a3b8')
        .linkDirectionalParticles(0)
        .linkCurvature(0.15);

      /* ── Click → navigate to domain ── */
      Graph.onNodeClick((nodeObj: NodeObject) => {
        const n = nodeObj as DNode;
        const { x: sx, y: sy } = Graph.graph2ScreenCoords(n.x || 0, n.y || 0, n.z || 0);
        const rect = containerRef.current?.getBoundingClientRect();
        const cx = (rect?.left || 0) + sx;
        const cy = (rect?.top || 0) + sy;

        setTransitioning({ domainId: n.id, cx, cy, color: n.color });
        transitionTimerRef.current = setTimeout(() => {
          if (mountedRef.current) navigateRef.current(`/domain/${n.id}`);
        }, TRANSITION_MS);
      });

      /* ── Hover cursor ── */
      Graph.onNodeHover((n: NodeObject | null) => {
        if (containerRef.current) containerRef.current.style.cursor = n ? 'pointer' : 'default';
      });

      /* ── Auto-rotate ── */
      const ctrl = Graph.controls() as any;
      if (ctrl) {
        ctrl.autoRotate = true;
        ctrl.autoRotateSpeed = 0.3;
        ctrl.enableDamping = true;
        ctrl.dampingFactor = 0.12;
      }

      /* ── Camera — position so the most-complete domain is roughly front-facing ── */
      // Initial camera: slightly elevated, looking at center (0,0,0)
      // The force simulation will place the top-completeness node somewhere on the sphere.
      // We wait for simulation warmup then nudge camera toward that node.
      Graph.cameraPosition({ x: 0, y: 80, z: 780 });

      // After simulation settles, rotate camera to face the most-complete domain
      setTimeout(() => {
        if (destroyed) return;
        const allNodes = Graph.graphData().nodes as DNode[];
        const topNode = allNodes.find(nd => nd.id === topDomainId);
        if (topNode && topNode.x != null && topNode.z != null) {
          // Position camera behind the top node, looking through it toward center
          const nx = topNode.x || 0, ny = topNode.y || 0, nz = topNode.z || 0;
          const dist = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
          // Camera at 780 units from center, in direction of the top node
          const camDist = 780;
          const scale = camDist / dist;
          Graph.cameraPosition(
            { x: nx * scale, y: ny * scale * 0.4 + 80, z: nz * scale },
            { x: 0, y: 0, z: 0 },
            1500 // smooth 1.5s transition
          );
        }
      }, 3000);

      /* ── Resize ── */
      const ro = new ResizeObserver((entries) => {
        for (const e of entries) {
          const { width, height } = e.contentRect;
          if (width && height) Graph.width(width).height(height);
        }
      });
      ro.observe(containerRef.current);

      graphRef.current = Graph;
    });

    return () => {
      destroyed = true;
      if (graphRef.current) {
        graphRef.current._destructor();
        graphRef.current = null;
      }
      for (const tex of _labelCache.values()) tex.dispose();
      _labelCache.clear();
    };
  }, [graphData, topDomainId]);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: BG_COLOR }}>
      <div ref={containerRef} className="absolute inset-0 w-full h-full" />

      {/* Header overlay */}
      <div className="absolute left-0 right-0 text-center pointer-events-none select-none" style={{ top: 28, zIndex: 10 }}>
        <h1 style={{
          fontSize: 26, fontWeight: 500, color: '#2a2a2a', letterSpacing: '-0.02em', marginBottom: 6,
          fontFamily: '"Noto Serif SC", "Source Serif 4", Georgia, serif',
          textShadow: '0 1px 8px rgba(232,232,228,0.9)',
        }}>
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 13, color: '#888', lineHeight: 1.6, textShadow: '0 1px 6px rgba(232,232,228,0.8)' }}>
          拖拽旋转 · 点击星球进入 3D 知识图谱
        </p>
      </div>

      {/* Loading */}
      {loading && activeDomains.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin" style={{ color: '#888' }} />
        </div>
      )}

      {/* Transition overlay */}
      {transitioning && (
        <div className="fixed inset-0" style={{ zIndex: 50, pointerEvents: 'none' }}>
          <div style={{
            position: 'absolute', left: transitioning.cx, top: transitioning.cy,
            width: 0, height: 0, borderRadius: '50%', backgroundColor: transitioning.color,
            transform: 'translate(-50%, -50%)',
            animation: `orb-expand ${TRANSITION_MS}ms cubic-bezier(0.4, 0, 0.2, 1) forwards`,
            opacity: 0.85,
          }} />
        </div>
      )}

      <style>{`
        @keyframes orb-expand {
          0% { width: 0; height: 0; opacity: 0.9; }
          100% { width: 300vmax; height: 300vmax; opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}

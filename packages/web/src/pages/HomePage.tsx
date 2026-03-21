import { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { peekDomainProgress } from '@/lib/store/learning';
import { fetchDomainLinks, type DomainLink } from '@/lib/api/graph-api';
import { Loader } from 'lucide-react';
import * as THREE from 'three';
import type { ForceGraph3DInstance } from '3d-force-graph';
import type { NodeObject, LinkObject } from '3d-force-graph';

/* ─── Demo fallback ─── */
const DEMO_DOMAINS: import('@akg/shared').Domain[] = [
  { id: 'ai-engineering', name: 'AI编程', description: '', color: '#8b5cf6', is_active: true, stats: { total_concepts: 400, total_edges: 615, subdomains: 15 } },
  { id: 'mathematics', name: '数学', description: '', color: '#3b82f6', is_active: true, stats: { total_concepts: 269, total_edges: 366, subdomains: 12 } },
  { id: 'game-engine', name: '游戏引擎', description: '', color: '#059669', is_active: true, stats: { total_concepts: 300, total_edges: 319, subdomains: 15 } },
  { id: 'game-design', name: '游戏设计', description: '', color: '#dc2626', is_active: true, stats: { total_concepts: 250, total_edges: 274, subdomains: 12 } },
  { id: 'psychology', name: '心理学', description: '', color: '#a855f7', is_active: true, stats: { total_concepts: 183, total_edges: 203, subdomains: 8 } },
  { id: 'physics', name: '物理', description: '', color: '#22c55e', is_active: true, stats: { total_concepts: 194, total_edges: 232, subdomains: 10 } },
  { id: 'english', name: '英语', description: '', color: '#eab308', is_active: true, stats: { total_concepts: 200, total_edges: 229, subdomains: 10 } },
];

/* ─── Display name overrides ─── */
const NAME_MAP: Record<string, string> = { 'ai-engineering': 'AI编程' };

/* ─── Constants ─── */
const BG = '#e8e8e4';
const SPHERE_R = 280;       // tighter sphere so bubbles cluster
const TRANSITION_MS = 900;
const LINK_THRESHOLD = 8;   // only very strong links shown

/* ─── Types ─── */
interface DomainProgress { mastered: number; learning: number; total: number }
interface DNode extends NodeObject {
  id: string; name: string; color: string;
  concepts: number; edges: number; subs: number;
  completeness: number;
  progress: DomainProgress;
}
interface DLink extends LinkObject<DNode> { count: number }

/* ─── Completeness → bubble radius (3D units) ─── */
function completeness(c: number, e: number, s: number) {
  return c + e * 0.5 + s * 5;
}
function bubbleR(n: DNode): number {
  // Range 28-65 — much larger than detail-page dots (3-5)
  const t = Math.max(0, Math.min(1, (n.completeness - 300) / 450));
  return 28 + t * 37;
}

/* ─── Build label texture with name + stats INSIDE the bubble ─── */
const _texCache = new Map<string, THREE.Texture>();
function labelTex(name: string, line2: string): THREE.Texture {
  const k = name + '|' + line2;
  if (_texCache.has(k)) return _texCache.get(k)!;
  const C = document.createElement('canvas');
  const X = C.getContext('2d')!;
  const F = '"Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif';
  const s1 = 96, s2 = 40;
  X.font = '700 ' + s1 + 'px ' + F;
  const w1 = X.measureText(name).width;
  X.font = '400 ' + s2 + 'px ' + F;
  const w2 = X.measureText(line2).width;
  const p = 48;
  const W = Math.ceil(Math.max(w1, w2)) + p * 2;
  const H = s1 + s2 + 20 + p;
  C.width = W; C.height = H;
  // Name
  X.font = '700 ' + s1 + 'px ' + F;
  X.textBaseline = 'top'; X.textAlign = 'center';
  X.fillStyle = 'rgba(255,255,255,0.95)';
  X.fillText(name, W / 2, p / 2);
  // Stats
  if (line2) {
    X.font = '400 ' + s2 + 'px ' + F;
    X.fillStyle = 'rgba(255,255,255,0.7)';
    X.fillText(line2, W / 2, p / 2 + s1 + 8);
  }
  const t = new THREE.CanvasTexture(C);
  t.minFilter = THREE.LinearFilter;
  t.magFilter = THREE.LinearFilter;
  _texCache.set(k, t);
  return t;
}

/* ═══════════════════════════════════════════
   HomePage - Dense bubble cluster, 3D rotatable
   ═══════════════════════════════════════════ */
export function HomePage() {
  const nav = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const active = domains.filter(d => d.is_active !== false);
  const cRef = useRef<HTMLDivElement>(null);
  const gRef = useRef<ForceGraph3DInstance | null>(null);
  const [links, setLinks] = useState<DomainLink[]>([]);
  const [trans, setTrans] = useState<{ id: string; cx: number; cy: number; color: string } | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);
  const navRef = useRef(nav); navRef.current = nav;

  useEffect(() => {
    fetchDomains().then(() => {
      if (useDomainStore.getState().domains.length === 0)
        useDomainStore.setState({ domains: DEMO_DOMAINS, loading: false, error: null });
    });
    fetchDomainLinks().then(setLinks).catch(() => {});
  }, [fetchDomains]);

  useEffect(() => { alive.current = true; return () => { alive.current = false; if (timerRef.current) clearTimeout(timerRef.current); }; }, []);

  const gd = useMemo(() => {
    if (!active.length) return null;
    const nodes: DNode[] = active.map(d => {
      const p = peekDomainProgress(d.id);
      const c = d.stats?.total_concepts ?? 0, e = d.stats?.total_edges ?? 0, s = d.stats?.subdomains ?? 0;
      if (c && p.total !== c) p.total = c;
      return { id: d.id, name: NAME_MAP[d.id] || d.name, color: d.color, concepts: c, edges: e, subs: s, completeness: completeness(c, e, s), progress: p };
    });
    nodes.sort((a, b) => b.completeness - a.completeness);
    const ids = new Set(nodes.map(n => n.id));
    const ll: DLink[] = links.filter(l => ids.has(l.source) && ids.has(l.target) && l.count >= LINK_THRESHOLD).map(l => ({ source: l.source, target: l.target, count: l.count }));
    return { nodes, links: ll };
  }, [active, links]);

  const topId = gd?.nodes[0]?.id;

  useEffect(() => {
    if (!cRef.current || !gd) return;
    let dead = false;

    import('3d-force-graph').then(({ default: FG3D }) => {
      if (dead || !cRef.current) return;
      const G = new FG3D(cRef.current, { controlType: 'orbit' });

      G.backgroundColor(BG).showNavInfo(false).graphData(gd as any);

      // Scene
      const sc = G.scene();
      sc.fog = new THREE.FogExp2(0xe8e8e4, 0.00008);

      // Lights - bright so translucent spheres look good
      G.lights([
        new THREE.AmbientLight(0xffffff, 1.6),
        (() => { const l = new THREE.DirectionalLight(0xffffff, 0.5); l.position.set(200, 400, 300); return l; })(),
        (() => { const l = new THREE.DirectionalLight(0xddd6fe, 0.3); l.position.set(-300, -100, 400); return l; })(),
      ]);

      // Forces: moderate charge so bubbles stay close but don't overlap
      // @ts-ignore
      G.d3Force('charge')?.strength(-300);
      // @ts-ignore
      G.d3Force('link')?.distance(80).strength(0.06);

      // Sphere-surface pull: keeps cluster roughly spherical
      G.onEngineTick(() => {
        const ns = G.graphData().nodes as DNode[];
        for (const n of ns) {
          if (n.x == null || n.y == null || n.z == null) continue;
          const d = Math.sqrt(n.x * n.x + n.y * n.y + n.z * n.z) || 1;
          const s = SPHERE_R / d;
          const pull = 0.015; // gentle - allows some depth variation
          n.x! += (n.x! * s - n.x!) * pull;
          n.y! += (n.y! * s - n.y!) * pull;
          n.z! += (n.z! * s - n.z!) * pull;
        }
      });

      // --- Custom node: big translucent bubble with text INSIDE ---
      G.nodeThreeObjectExtend(false) // fully replace default node
        .nodeThreeObject((obj: object) => {
          const n = obj as DNode;
          const R = bubbleR(n);
          const group = new THREE.Group();

          // --- Main bubble sphere ---
          const col = new THREE.Color(n.color);
          const geo = new THREE.SphereGeometry(R, 48, 48);
          const mat = new THREE.MeshPhysicalMaterial({
            color: col, transparent: true, opacity: 0.55,
            roughness: 0.15, metalness: 0.0,
            clearcoat: 0.8, clearcoatRoughness: 0.1,
            side: THREE.FrontSide, depthWrite: false,
          });
          group.add(new THREE.Mesh(geo, mat));

          // --- Soft glow halo ---
          const glowGeo = new THREE.SphereGeometry(R * 1.18, 24, 24);
          const glowMat = new THREE.MeshBasicMaterial({
            color: col, transparent: true, opacity: 0.12,
            side: THREE.BackSide, depthWrite: false,
          });
          group.add(new THREE.Mesh(glowGeo, glowMat));

          // --- Label sprite inside bubble ---
          const info: string[] = [];
          if (n.concepts) info.push(n.concepts + ' 知识点');
          if (n.subs) info.push(n.subs + ' 子领域');
          const tex = labelTex(n.name, info.join(' \u00b7 '));
          const sm = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 1, depthWrite: false, depthTest: false });
          const sp = new THREE.Sprite(sm);
          const img = tex.image as { width: number; height: number };
          const asp = img.width / img.height;
          // Scale label to fit ~80% of bubble diameter
          const lH = R * 0.9;
          sp.scale.set(lH * asp, lH, 1);
          sp.position.set(0, 0, 0);
          sp.renderOrder = 10;
          group.add(sp);

          return group;
        })
        .nodeLabel('');

      // Links: very subtle
      G.linkWidth(0.5).linkOpacity(0.1).linkColor(() => '#b0b0b0')
        .linkDirectionalParticles(0).linkCurvature(0.2);

      // Click
      G.onNodeClick((obj: NodeObject) => {
        const n = obj as DNode;
        const { x: sx, y: sy } = G.graph2ScreenCoords(n.x || 0, n.y || 0, n.z || 0);
        const r = cRef.current?.getBoundingClientRect();
        setTrans({ id: n.id, cx: (r?.left || 0) + sx, cy: (r?.top || 0) + sy, color: n.color });
        timerRef.current = setTimeout(() => { if (alive.current) navRef.current('/domain/' + n.id); }, TRANSITION_MS);
      });

      G.onNodeHover((n: NodeObject | null) => { if (cRef.current) cRef.current.style.cursor = n ? 'pointer' : 'default'; });

      // Auto-rotate
      const ctrl = G.controls() as any;
      if (ctrl) { ctrl.autoRotate = true; ctrl.autoRotateSpeed = 0.25; ctrl.enableDamping = true; ctrl.dampingFactor = 0.12; }

      // Camera
      G.cameraPosition({ x: 0, y: 60, z: 620 });

      // After warmup, pan to face the most-complete domain
      setTimeout(() => {
        if (dead) return;
        const ns = G.graphData().nodes as DNode[];
        const top = ns.find(nd => nd.id === topId);
        if (top?.x != null && top.z != null) {
          const nx = top.x || 0, ny = top.y || 0, nz = top.z || 0;
          const d = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
          const s = 620 / d;
          G.cameraPosition({ x: nx * s, y: ny * s * 0.3 + 60, z: nz * s }, { x: 0, y: 0, z: 0 }, 1500);
        }
      }, 3000);

      // Resize
      const ro = new ResizeObserver(es => { for (const e of es) { const { width: w, height: h } = e.contentRect; if (w && h) G.width(w).height(h); } });
      ro.observe(cRef.current);
      gRef.current = G;
    });

    return () => {
      dead = true;
      if (gRef.current) { gRef.current._destructor(); gRef.current = null; }
      for (const t of _texCache.values()) t.dispose();
      _texCache.clear();
    };
  }, [gd, topId]);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: BG }}>
      <div ref={cRef} className="absolute inset-0 w-full h-full" />
      {/* Header */}
      <div className="absolute left-0 right-0 text-center pointer-events-none select-none" style={{ top: 28, zIndex: 10 }}>
        <h1 style={{ fontSize: 26, fontWeight: 500, color: '#2a2a2a', letterSpacing: '-0.02em', marginBottom: 6, fontFamily: '"Noto Serif SC","Source Serif 4",Georgia,serif', textShadow: '0 1px 8px rgba(232,232,228,0.9)' }}>
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 13, color: '#888', lineHeight: 1.6, textShadow: '0 1px 6px rgba(232,232,228,0.8)' }}>
          拖拽旋转 · 点击星球进入 3D 知识图谱
        </p>
      </div>
      {/* Loading */}
      {loading && active.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin" style={{ color: '#888' }} />
        </div>
      )}
      {/* Transition */}
      {trans && (
        <div className="fixed inset-0" style={{ zIndex: 50, pointerEvents: 'none' }}>
          <div style={{ position: 'absolute', left: trans.cx, top: trans.cy, width: 0, height: 0, borderRadius: '50%', backgroundColor: trans.color, transform: 'translate(-50%,-50%)', animation: 'orb-expand ' + TRANSITION_MS + 'ms cubic-bezier(0.4,0,0.2,1) forwards', opacity: 0.85 }} />
        </div>
      )}
      <style>{`@keyframes orb-expand { 0% { width:0;height:0;opacity:0.9 } 100% { width:300vmax;height:300vmax;opacity:0.4 } }`}</style>
    </div>
  );
}

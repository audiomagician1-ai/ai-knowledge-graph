import { useEffect, useRef, useCallback, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { peekDomainProgress } from '@/lib/store/learning';
import { Loader } from 'lucide-react';

/* ─── Resolved CSS variable cache (canvas can't read CSS vars directly) ─── */
let _resolvedColors: { surface0: string; textPrimary: string; textTertiary: string } | null = null;
function getThemeColors(): { surface0: string; textPrimary: string; textTertiary: string } {
  if (_resolvedColors) return _resolvedColors;
  if (typeof document === 'undefined') return { surface0: '#f0f0ed', textPrimary: '#1a1a1a', textTertiary: '#888888' };
  const s = getComputedStyle(document.documentElement);
  _resolvedColors = {
    surface0: s.getPropertyValue('--color-surface-0').trim() || '#f0f0ed',
    textPrimary: s.getPropertyValue('--color-text-primary').trim() || '#1a1a1a',
    textTertiary: s.getPropertyValue('--color-text-tertiary').trim() || '#888888',
  };
  return _resolvedColors;
}

/* ─── Types ─── */
interface DomainProgress {
  mastered: number;
  learning: number;
  total: number; // from seed stats — total concepts in domain
}

interface Orb {
  x: number; y: number; z: number;
  vx: number; vy: number; vz: number;
  radius: number;
  color: string;
  glowColor: string;
  domain: import('@akg/shared').Domain;
  hovered: boolean;
  stats?: import('@akg/shared').DomainStats;
  progress?: DomainProgress;
  /** Pre-generated mini-graph nodes inside this orb (sphere-surface distribution) */
  miniNodes?: MiniNode[];
  /** Pre-generated mini-graph edges (index pairs) */
  miniEdges?: [number, number][];
}

interface BgNode {
  x: number; y: number; z: number;
  vx: number; vy: number; vz: number;
  size: number;
  opacity: number;
  /** Hub nodes are larger, colored, and more connected */
  isHub: boolean;
  /** Muted color tint — hue varies per node for visual richness */
  hue: number;
}

/** A tiny node on the surface of a mini knowledge-graph sphere inside an orb */
interface MiniNode {
  /** Spherical coords — theta (azimuth), phi (polar) */
  theta: number; phi: number;
  size: number;
  /** Brightness variation 0-1 */
  brightness: number;
}

/* ─── Demo domains used when backend is not available (dev preview) ─── */
const DEMO_DOMAINS: import('@akg/shared').Domain[] = [
  { id: 'psychology', name: '心理学', description: '心理学知识领域', icon: '💜', color: '#9b59b6', is_active: true, stats: { total_concepts: 183, total_edges: 400, subdomains: 8 } },
  { id: 'ai-engineering', name: 'AI工程', description: 'AI工程知识领域', icon: '🤖', color: '#8e44ad', is_active: true, stats: { total_concepts: 403, total_edges: 800, subdomains: 15 } },
  { id: 'finance', name: '金融理财', description: '金融理财知识领域', icon: '💰', color: '#e67e22', is_active: true, stats: { total_concepts: 160, total_edges: 320, subdomains: 8 } },
  { id: 'product-design', name: '产品设计', description: '产品设计知识领域', icon: '🎨', color: '#e74c3c', is_active: true, stats: { total_concepts: 182, total_edges: 350, subdomains: 9 } },
  { id: 'mathematics', name: '数学', description: '数学知识领域', icon: '📐', color: '#3498db', is_active: true, stats: { total_concepts: 209, total_edges: 500, subdomains: 12 } },
  { id: 'english', name: '英语', description: '英语知识领域', icon: '🌟', color: '#f1c40f', is_active: true, stats: { total_concepts: 200, total_edges: 400, subdomains: 10 } },
  { id: 'physics', name: '物理', description: '物理知识领域', icon: '🔬', color: '#2ecc71', is_active: true, stats: { total_concepts: 194, total_edges: 380, subdomains: 10 } },
];

/* ─── Constants ─── */
const BG_NODE_COUNT = 200;
const BG_HUB_COUNT = 18;
const BG_CONNECTION_DIST = 260;
const ORB_BASE_RADIUS = 57;
const PERSPECTIVE = 600;
const Z_RANGE = 200;
const FLOAT_SPEED = 0.0004;
const TRANSITION_MS = 900;
const MINI_NODE_COUNT = 50;
const MINI_EDGE_MAX = 40;

/* ─── Helpers ─── */
function hexToRgba(hex: string, a: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${a})`;
}

function hexToRgb(hex: string): [number, number, number] {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];
}

function project(x: number, y: number, z: number, cx: number, cy: number): { sx: number; sy: number; scale: number } {
  const scale = PERSPECTIVE / (PERSPECTIVE + z);
  return { sx: cx + x * scale, sy: cy + y * scale, scale };
}

/** Pseudo-random seeded by index — deterministic mini-graph layout */
function seededRandom(seed: number): number {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

/** Generate mini-graph nodes distributed on a sphere surface (Fibonacci lattice) */
function generateMiniGraph(): { nodes: MiniNode[]; edges: [number, number][] } {
  const nodes: MiniNode[] = [];
  const goldenAngle = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < MINI_NODE_COUNT; i++) {
    const theta = goldenAngle * i;
    const phi = Math.acos(1 - 2 * (i + 0.5) / MINI_NODE_COUNT);
    nodes.push({
      theta,
      phi,
      size: 0.8 + seededRandom(i * 7 + 3) * 1.8,
      brightness: 0.5 + seededRandom(i * 13 + 5) * 0.5,
    });
  }
  // Connect nearby nodes on the sphere
  const edges: [number, number][] = [];
  for (let i = 0; i < MINI_NODE_COUNT && edges.length < MINI_EDGE_MAX; i++) {
    const xi = Math.sin(nodes[i].phi) * Math.cos(nodes[i].theta);
    const yi = Math.sin(nodes[i].phi) * Math.sin(nodes[i].theta);
    const zi = Math.cos(nodes[i].phi);
    for (let j = i + 1; j < MINI_NODE_COUNT && edges.length < MINI_EDGE_MAX; j++) {
      const xj = Math.sin(nodes[j].phi) * Math.cos(nodes[j].theta);
      const yj = Math.sin(nodes[j].phi) * Math.sin(nodes[j].theta);
      const zj = Math.cos(nodes[j].phi);
      const dist = Math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2 + (zi - zj) ** 2);
      if (dist < 0.85) edges.push([i, j]);
    }
  }
  return { nodes, edges };
}

/* ─── Background network canvas (graph-page style, dimmed) ─── */
function drawBackground(
  ctx: CanvasRenderingContext2D,
  w: number, h: number,
  nodes: BgNode[],
  time: number,
) {
  // Soft warm gradient background
  const grad = ctx.createLinearGradient(0, 0, w, h);
  grad.addColorStop(0, '#e8e8e3');
  grad.addColorStop(0.5, '#eae9e4');
  grad.addColorStop(1, '#e5e4df');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, w, h);

  // Subtle radial vignette
  const vg = ctx.createRadialGradient(w / 2, h / 2, w * 0.15, w / 2, h / 2, w * 0.75);
  vg.addColorStop(0, 'rgba(255,255,255,0.12)');
  vg.addColorStop(1, 'rgba(0,0,0,0.05)');
  ctx.fillStyle = vg;
  ctx.fillRect(0, 0, w, h);

  // Move nodes (3D drift)
  for (const n of nodes) {
    n.x += n.vx + Math.sin(time * 0.0003 + n.z * 0.01) * 0.04;
    n.y += n.vy + Math.cos(time * 0.00025 + n.x * 0.005) * 0.03;
    n.z += n.vz;
    // Wrap around
    if (n.x < -40) n.x = w + 40;
    if (n.x > w + 40) n.x = -40;
    if (n.y < -40) n.y = h + 40;
    if (n.y > h + 40) n.y = -40;
    if (n.z < -300) n.z = 300;
    if (n.z > 300) n.z = -300;
    // Depth-based opacity modulation (closer = slightly brighter)
    const depthFactor = 0.3 + 0.7 * ((300 - n.z) / 600);
    n.opacity = (0.25 + 0.12 * Math.sin(time * 0.0008 + n.hue * 3)) * depthFactor;
  }

  // Draw connections — graph-page style with varied thickness
  for (let i = 0; i < nodes.length; i++) {
    const ni = nodes[i];
    for (let j = i + 1; j < nodes.length; j++) {
      const nj = nodes[j];
      const dx = ni.x - nj.x;
      const dy = ni.y - nj.y;
      const dist2d = Math.sqrt(dx * dx + dy * dy);
      const dz = Math.abs(ni.z - nj.z);
      // Only connect nodes that are close in 2D AND not too far in depth
      if (dist2d < BG_CONNECTION_DIST && dz < 200) {
        const distFactor = 1 - dist2d / BG_CONNECTION_DIST;
        const depthAlpha = 1 - dz / 200;
        // Hub-to-hub connections are slightly thicker
        const isHubLink = ni.isHub || nj.isHub;
        const alpha = distFactor * depthAlpha * (isHubLink ? 0.25 : 0.14);
        if (alpha < 0.005) continue;
        ctx.strokeStyle = `rgba(130,128,120,${alpha})`;
        ctx.lineWidth = isHubLink ? 1.2 : 0.7;
        ctx.beginPath();
        ctx.moveTo(ni.x, ni.y);
        ctx.lineTo(nj.x, nj.y);
        ctx.stroke();
      }
    }
  }

  // Draw nodes — varied sizes, muted color tints
  for (const n of nodes) {
    if (n.opacity < 0.01) continue;
    if (n.isHub) {
      // Hub nodes: larger with subtle color tint
      const h = n.hue * 360;
      ctx.fillStyle = `hsla(${h}, 25%, 45%, ${n.opacity * 2.5})`;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.size, 0, Math.PI * 2);
      ctx.fill();
      // Tiny glow around hubs
      const hubGlow = ctx.createRadialGradient(n.x, n.y, n.size * 0.5, n.x, n.y, n.size * 3);
      hubGlow.addColorStop(0, `hsla(${h}, 30%, 50%, ${n.opacity * 1.2})`);
      hubGlow.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = hubGlow;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.size * 3, 0, Math.PI * 2);
      ctx.fill();
    } else {
      // Regular nodes: tiny dots
      ctx.fillStyle = `rgba(140,138,130,${n.opacity * 1.8})`;
      ctx.beginPath();
      ctx.arc(n.x, n.y, n.size, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

/* ─── Draw mini knowledge-graph sphere inside an orb ─── */
function drawMiniGraph(
  ctx: CanvasRenderingContext2D,
  sx: number, sy: number,
  finalR: number,
  miniNodes: MiniNode[],
  miniEdges: [number, number][],
  color: string,
  time: number,
  orbSeed: number,
  hovered: boolean,
) {
  const [cr, cg, cb] = hexToRgb(color);
  const sphereR = finalR * 0.82;
  // Slow rotation
  const rotY = time * 0.0003 + orbSeed;
  const rotX = Math.sin(time * 0.0002 + orbSeed * 2) * 0.2;
  const cosY = Math.cos(rotY), sinY = Math.sin(rotY);
  const cosX = Math.cos(rotX), sinX = Math.sin(rotX);

  // Project each mini-node to 2D
  const projected: { x: number; y: number; z: number; size: number; brightness: number }[] = [];
  for (const mn of miniNodes) {
    // Sphere surface → 3D
    let nx = Math.sin(mn.phi) * Math.cos(mn.theta) * sphereR;
    let ny = Math.sin(mn.phi) * Math.sin(mn.theta) * sphereR;
    let nz = Math.cos(mn.phi) * sphereR;
    // Rotate Y
    const tx = nx * cosY - nz * sinY;
    const tz = nx * sinY + nz * cosY;
    nx = tx; nz = tz;
    // Rotate X
    const ty = ny * cosX - nz * sinX;
    const tz2 = ny * sinX + nz * cosX;
    ny = ty; nz = tz2;
    projected.push({ x: sx + nx, y: sy + ny, z: nz, size: mn.size, brightness: mn.brightness });
  }

  // Sort by z (back to front) for proper layering
  const sortedIdx = projected.map((_, i) => i).sort((a, b) => projected[a].z - projected[b].z);

  // Draw edges — back hemisphere dimmer, front brighter
  const edgeAlphaBase = hovered ? 0.55 : 0.4;
  for (const [i, j] of miniEdges) {
    const a = projected[i], b = projected[j];
    const avgZ = (a.z + b.z) / 2;
    const frontness = (avgZ + sphereR) / (sphereR * 2); // 0=back, 1=front
    const edgeAlpha = edgeAlphaBase * (0.1 + frontness * 0.9);
    if (edgeAlpha < 0.02) continue;
    ctx.strokeStyle = `rgba(${cr},${cg},${cb},${edgeAlpha})`;
    ctx.lineWidth = hovered ? 1.0 : 0.7;
    ctx.beginPath();
    ctx.moveTo(a.x, a.y);
    ctx.lineTo(b.x, b.y);
    ctx.stroke();
  }

  // Draw nodes — back hemisphere dim, front hemisphere bright + glow
  for (const idx of sortedIdx) {
    const p = projected[idx];
    const frontness = (p.z + sphereR) / (sphereR * 2); // 0=back, 1=front
    const nodeAlpha = (hovered ? 0.85 : 0.65) * (0.1 + frontness * 0.9) * p.brightness;
    if (nodeAlpha < 0.02) continue;
    const dotR = p.size * (0.6 + frontness * 0.9) * (hovered ? 1.2 : 1);
    // Brighter core color
    const nr = Math.min(255, cr + 60);
    const ng = Math.min(255, cg + 60);
    const nb = Math.min(255, cb + 60);
    // Subtle glow around front-facing nodes
    if (frontness > 0.5 && dotR > 1.2) {
      const glowAlpha = nodeAlpha * 0.35;
      const nodeGlow = ctx.createRadialGradient(p.x, p.y, dotR * 0.3, p.x, p.y, dotR * 3);
      nodeGlow.addColorStop(0, `rgba(${nr},${ng},${nb},${glowAlpha})`);
      nodeGlow.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = nodeGlow;
      ctx.beginPath();
      ctx.arc(p.x, p.y, dotR * 3, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.fillStyle = `rgba(${nr},${ng},${nb},${nodeAlpha})`;
    ctx.beginPath();
    ctx.arc(p.x, p.y, dotR, 0, Math.PI * 2);
    ctx.fill();
  }
}

/* ─── Draw a single knowledge orb ─── */
function drawOrb(
  ctx: CanvasRenderingContext2D,
  orb: Orb,
  cx: number, cy: number,
  time: number,
) {
  const { sx, sy, scale } = project(orb.x, orb.y, orb.z, cx, cy);
  const r = orb.radius * scale;
  const hoverScale = orb.hovered ? 1.15 : 1;
  const finalR = r * hoverScale;

  // Outer glow — soft colored halo
  const glowR = finalR * (orb.hovered ? 3.0 : 2.4);
  const glow = ctx.createRadialGradient(sx, sy, finalR * 0.5, sx, sy, glowR);
  glow.addColorStop(0, hexToRgba(orb.color, orb.hovered ? 0.20 : 0.10));
  glow.addColorStop(0.5, hexToRgba(orb.color, orb.hovered ? 0.06 : 0.03));
  glow.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(sx, sy, glowR, 0, Math.PI * 2);
  ctx.fill();

  // Sphere body — soft center, fading to transparent at edge (no hard boundary)
  const bodyR = finalR * 1.15; // slightly larger so the fade happens outside the visual center
  const bodyGrad = ctx.createRadialGradient(sx, sy, 0, sx, sy, bodyR);
  bodyGrad.addColorStop(0, hexToRgba(orb.glowColor, 0.22));
  bodyGrad.addColorStop(0.35, hexToRgba(orb.color, 0.15));
  bodyGrad.addColorStop(0.65, hexToRgba(orb.color, 0.10));
  bodyGrad.addColorStop(0.85, hexToRgba(orb.color, 0.04));
  bodyGrad.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = bodyGrad;
  ctx.beginPath();
  ctx.arc(sx, sy, bodyR, 0, Math.PI * 2);
  ctx.fill();

  // Draw mini knowledge-graph sphere inside the orb (main visual)
  if (orb.miniNodes && orb.miniEdges) {
    ctx.save();
    ctx.beginPath();
    ctx.arc(sx, sy, finalR * 0.96, 0, Math.PI * 2);
    ctx.clip();
    drawMiniGraph(ctx, sx, sy, finalR, orb.miniNodes, orb.miniEdges, orb.color, time, orb.x + orb.y, orb.hovered);
    ctx.restore();
  }

  // Subtle specular — very light, small, no hard edge
  const specGrad = ctx.createRadialGradient(
    sx - finalR * 0.2, sy - finalR * 0.25, 0,
    sx - finalR * 0.2, sy - finalR * 0.25, finalR * 0.45,
  );
  specGrad.addColorStop(0, 'rgba(255,255,255,0.18)');
  specGrad.addColorStop(0.6, 'rgba(255,255,255,0.03)');
  specGrad.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = specGrad;
  ctx.beginPath();
  ctx.arc(sx, sy, finalR, 0, Math.PI * 2);
  ctx.fill();

  // Domain name — centered inside the orb
  const tc = getThemeColors();
  const fontSize = Math.round(finalR * 0.32);
  ctx.font = `600 ${fontSize}px "Noto Serif SC", "Source Serif 4", Georgia, serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  // Subtle text shadow for readability over the mini-graph
  ctx.fillStyle = 'rgba(255,255,255,0.6)';
  ctx.fillText(orb.domain.name, sx + 0.5, sy + 0.5);
  ctx.fillStyle = orb.hovered ? tc.textPrimary : 'rgba(26,26,26,0.85)';
  ctx.fillText(orb.domain.name, sx, sy);

  // Stats line — below the name, still inside the orb
  if (orb.stats) {
    const statsY = sy + fontSize * 0.75;
    const statsFontSize = Math.round(finalR * 0.18);
    ctx.font = `400 ${statsFontSize}px "Inter", sans-serif`;
    ctx.fillStyle = `rgba(60,60,60,${orb.hovered ? 0.7 : 0.5})`;
    const parts: string[] = [];
    if (orb.stats.total_concepts != null) parts.push(`${orb.stats.total_concepts} 知识点`);
    if (orb.stats.subdomains != null) parts.push(`${orb.stats.subdomains} 子领域`);
    if (parts.length) ctx.fillText(parts.join(' · '), sx, statsY);
  }

  return { sx, sy, finalR, scale };
}

/* ─── Inter-orb connection lines ─── */
function drawOrbConnections(
  ctx: CanvasRenderingContext2D,
  orbs: Orb[],
  cx: number, cy: number,
  time: number,
) {
  for (let i = 0; i < orbs.length; i++) {
    const a = project(orbs[i].x, orbs[i].y, orbs[i].z, cx, cy);
    for (let j = i + 1; j < orbs.length; j++) {
      const b = project(orbs[j].x, orbs[j].y, orbs[j].z, cx, cy);
      const dx = a.sx - b.sx;
      const dy = a.sy - b.sy;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 400) {
        const alpha = (1 - dist / 400) * 0.06;
        // Animated dash
        ctx.strokeStyle = `rgba(100,100,95,${alpha})`;
        ctx.lineWidth = 1;
        ctx.setLineDash([3, 6]);
        ctx.lineDashOffset = -time * 0.02;
        ctx.beginPath();
        ctx.moveTo(a.sx, a.sy);
        ctx.lineTo(b.sx, b.sy);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }
  }
}

/* ═══════════════════════════════════════════
   HomePage Component
   ═══════════════════════════════════════════ */
export function HomePage() {
  const navigate = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const activeDomains = useMemo(
    () => domains.filter((d) => d.is_active !== false),
    [domains],
  );

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const bgNodesRef = useRef<BgNode[]>([]);
  const orbsRef = useRef<Orb[]>([]);
  const mouseRef = useRef<{ x: number; y: number }>({ x: -9999, y: -9999 });
  const [transitioning, setTransitioning] = useState<{ domainId: string; cx: number; cy: number; color: string } | null>(null);
  const transitionTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    fetchDomains().then(() => {
      // If no domains loaded (backend unavailable), use demo data
      const state = useDomainStore.getState();
      if (state.domains.length === 0) {
        useDomainStore.setState({ domains: DEMO_DOMAINS, loading: false, error: null });
      }
    });
  }, [fetchDomains]);

  // Cleanup on unmount — cancel pending transition timeout
  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      if (transitionTimerRef.current) clearTimeout(transitionTimerRef.current);
    };
  }, []);

  // Init background nodes — graph-page style with hub/spoke structure
  const initBgNodes = useCallback((w: number, h: number) => {
    const nodes: BgNode[] = [];
    // Hub nodes — larger, colored, scattered
    for (let i = 0; i < BG_HUB_COUNT; i++) {
      nodes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        z: (Math.random() - 0.5) * 400,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.15,
        vz: (Math.random() - 0.5) * 0.05,
        size: 3.5 + Math.random() * 3.5,
        opacity: 0.08,
        isHub: true,
        hue: Math.random(),
      });
    }
    // Regular nodes — tiny, more numerous
    for (let i = 0; i < BG_NODE_COUNT - BG_HUB_COUNT; i++) {
      nodes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        z: (Math.random() - 0.5) * 400,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
        vz: (Math.random() - 0.5) * 0.06,
        size: 1.2 + Math.random() * 2.0,
        opacity: 0.06,
        isHub: false,
        hue: Math.random(),
      });
    }
    bgNodesRef.current = nodes;
  }, []);

  // Init orbs from domains — arrange in a loose ellipse + generate mini-graphs
  useEffect(() => {
    if (activeDomains.length === 0) return;
    const count = activeDomains.length;
    const orbs: Orb[] = activeDomains.map((domain, i) => {
      const angle = (i / count) * Math.PI * 2 - Math.PI / 2;
      const rx = Math.min(420, 160 + count * 24);
      const ry = Math.min(300, 110 + count * 18);
      const jitterX = (Math.random() - 0.5) * 40;
      const jitterY = (Math.random() - 0.5) * 30;
      const stats = domain.stats;

      // Lighten color for glow
      const r = parseInt(domain.color.slice(1, 3), 16);
      const g = parseInt(domain.color.slice(3, 5), 16);
      const b = parseInt(domain.color.slice(5, 7), 16);
      const glowColor = `#${Math.min(255, r + 60).toString(16).padStart(2, '0')}${Math.min(255, g + 60).toString(16).padStart(2, '0')}${Math.min(255, b + 60).toString(16).padStart(2, '0')}`;

      // Generate unique mini-graph for this orb
      const { nodes: miniNodes, edges: miniEdges } = generateMiniGraph();

      return {
        x: Math.cos(angle) * rx + jitterX,
        y: Math.sin(angle) * ry + jitterY,
        z: (Math.random() - 0.5) * Z_RANGE,
        vx: (Math.random() - 0.5) * 0.15,
        vy: (Math.random() - 0.5) * 0.15,
        vz: (Math.random() - 0.5) * 0.08,
        radius: ORB_BASE_RADIUS + (stats?.total_concepts ? Math.min(12, stats.total_concepts / 40) : 0),
        color: domain.color,
        glowColor,
        domain,
        hovered: false,
        stats,
        miniNodes,
        miniEdges,
      };
    });
    orbsRef.current = orbs;
  }, [activeDomains]);

  // Canvas animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let w = 0, h = 0;
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth;
      h = canvas.clientHeight;
      canvas.width = w * dpr;
      canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      if (bgNodesRef.current.length === 0) initBgNodes(w, h);
    };
    resize();
    window.addEventListener('resize', resize);

    const tick = (time: number) => {
      ctx.clearRect(0, 0, w, h);

      // Background network
      drawBackground(ctx, w, h, bgNodesRef.current, time);

      const cx = w / 2;
      const cy = h / 2 + 20; // push orbs slightly below center for header space
      const orbs = orbsRef.current;

      // Float orbs
      for (const orb of orbs) {
        orb.x += orb.vx + Math.sin(time * FLOAT_SPEED + orb.z) * 0.12;
        orb.y += orb.vy + Math.cos(time * FLOAT_SPEED * 0.8 + orb.x * 0.01) * 0.1;
        orb.z += orb.vz;
        // Soft boundary bounce
        const boundX = Math.max(300, w * 0.35), boundY = Math.max(200, h * 0.28), boundZ = Z_RANGE;
        if (Math.abs(orb.x) > boundX) orb.vx *= -0.8;
        if (Math.abs(orb.y) > boundY) orb.vy *= -0.8;
        if (Math.abs(orb.z) > boundZ) orb.vz *= -0.8;
        // Damping
        orb.vx *= 0.9995;
        orb.vy *= 0.9995;
        orb.vz *= 0.9995;
      }

      // Hit-test mouse for hover
      const mx = mouseRef.current.x;
      const my = mouseRef.current.y;
      let anyHovered = false;
      for (const orb of orbs) {
        const { sx, sy, scale } = project(orb.x, orb.y, orb.z, cx, cy);
        const r = orb.radius * scale;
        const dx = mx - sx, dy = my - sy;
        orb.hovered = (dx * dx + dy * dy) < (r + 8) * (r + 8);
        if (orb.hovered) anyHovered = true;
      }
      cursorRef.current = anyHovered;

      // Sort by z (back to front)
      const sorted = [...orbs].sort((a, b) => b.z - a.z);

      // Draw connections between orbs
      drawOrbConnections(ctx, sorted, cx, cy, time);

      // Draw each orb
      for (const orb of sorted) {
        drawOrb(ctx, orb, cx, cy, time);
      }

      animRef.current = requestAnimationFrame(tick);
    };

    animRef.current = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(animRef.current);
      window.removeEventListener('resize', resize);
    };
  }, [initBgNodes]);

  // Mouse tracking + click
  const handlePointerMove = useCallback((e: React.PointerEvent) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    mouseRef.current = { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }, []);

  const handleClick = useCallback((e: React.MouseEvent) => {
    if (transitioning) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const cx = rect.width / 2;
    const cy = rect.height / 2 + 20;

    for (const orb of orbsRef.current) {
      const { sx, sy, scale } = project(orb.x, orb.y, orb.z, cx, cy);
      const r = orb.radius * scale;
      const dx = mx - sx, dy = my - sy;
      if (dx * dx + dy * dy < (r + 8) * (r + 8)) {
        // Trigger transition
        setTransitioning({ domainId: orb.domain.id, cx: e.clientX, cy: e.clientY, color: orb.color });
        transitionTimerRef.current = setTimeout(() => {
          if (mountedRef.current) navigate(`/domain/${orb.domain.id}`);
        }, TRANSITION_MS);
        return;
      }
    }
  }, [navigate, transitioning]);

  // Cursor style — derived from orb hover state each frame (via ref, set in rAF)
  const [cursorPointer, setCursorPointer] = useState(false);
  const cursorRef = useRef(false);
  // Sync cursorRef → state at low frequency to avoid re-renders every frame
  useEffect(() => {
    const id = setInterval(() => {
      if (cursorRef.current !== cursorPointer) setCursorPointer(cursorRef.current);
    }, 100);
    return () => clearInterval(id);
  }, [cursorPointer]);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      {/* Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ cursor: cursorPointer ? 'pointer' : 'default' }}
        onPointerMove={handlePointerMove}
        onClick={handleClick}
      />

      {/* Header overlay — top center */}
      <div
        className="absolute left-0 right-0 text-center pointer-events-none select-none"
        style={{ top: 40, zIndex: 10 }}
      >
        <h1
          style={{
            fontSize: 28,
            fontWeight: 500,
            color: 'var(--color-text-primary)',
            letterSpacing: '-0.02em',
            marginBottom: 8,
            fontFamily: '"Noto Serif SC", "Source Serif 4", Georgia, serif',
          }}
        >
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 14, color: 'var(--color-text-tertiary)', lineHeight: 1.6 }}>
          点击星球，进入 3D 知识图谱
        </p>
      </div>

      {/* Loading state */}
      {loading && activeDomains.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
        </div>
      )}

      {/* Transition overlay — expanding circle from click point */}
      {transitioning && (
        <div
          className="fixed inset-0"
          style={{ zIndex: 50, pointerEvents: 'none' }}
        >
          <div
            style={{
              position: 'absolute',
              left: transitioning.cx,
              top: transitioning.cy,
              width: 0,
              height: 0,
              borderRadius: '50%',
              backgroundColor: transitioning.color,
              transform: 'translate(-50%, -50%)',
              animation: `orb-expand ${TRANSITION_MS}ms cubic-bezier(0.4, 0, 0.2, 1) forwards`,
              opacity: 0.85,
            }}
          />
        </div>
      )}

      {/* Inline keyframes for transition */}
      <style>{`
        @keyframes orb-expand {
          0% { width: 0; height: 0; opacity: 0.9; }
          100% { width: 300vmax; height: 300vmax; opacity: 0.4; }
        }
      `}</style>
    </div>
  );
}

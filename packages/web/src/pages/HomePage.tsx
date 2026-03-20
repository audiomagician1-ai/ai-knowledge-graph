import { useEffect, useRef, useCallback, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { Loader } from 'lucide-react';

/* ─── Types ─── */
interface Orb {
  x: number; y: number; z: number;
  vx: number; vy: number; vz: number;
  radius: number;
  color: string;
  glowColor: string;
  domain: import('@akg/shared').Domain;
  hovered: boolean;
  stats?: { total_concepts?: number; subdomains?: number };
}

interface BgNode { x: number; y: number; vx: number; vy: number; size: number; opacity: number }

/* ─── Constants ─── */
const BG_NODE_COUNT = 90;
const CONNECTION_DIST = 180;
const ORB_BASE_RADIUS = 38;
const PERSPECTIVE = 600;
const Z_RANGE = 200;
const FLOAT_SPEED = 0.0004;
const TRANSITION_MS = 900;

/* ─── Helpers ─── */
function hexToRgba(hex: string, a: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${a})`;
}

function project(x: number, y: number, z: number, cx: number, cy: number): { sx: number; sy: number; scale: number } {
  const scale = PERSPECTIVE / (PERSPECTIVE + z);
  return { sx: cx + x * scale, sy: cy + y * scale, scale };
}

/* ─── Background network canvas ─── */
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
  vg.addColorStop(0, 'rgba(255,255,255,0.15)');
  vg.addColorStop(1, 'rgba(0,0,0,0.04)');
  ctx.fillStyle = vg;
  ctx.fillRect(0, 0, w, h);

  // Move nodes
  for (const n of nodes) {
    n.x += n.vx;
    n.y += n.vy;
    if (n.x < -20) n.x = w + 20;
    if (n.x > w + 20) n.x = -20;
    if (n.y < -20) n.y = h + 20;
    if (n.y > h + 20) n.y = -20;
    n.opacity = 0.12 + 0.08 * Math.sin(time * 0.001 + n.x * 0.01);
  }

  // Draw connections
  ctx.lineWidth = 0.5;
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < CONNECTION_DIST) {
        const alpha = (1 - dist / CONNECTION_DIST) * 0.08;
        ctx.strokeStyle = `rgba(120,118,112,${alpha})`;
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.stroke();
      }
    }
  }

  // Draw nodes
  for (const n of nodes) {
    ctx.fillStyle = `rgba(140,138,130,${n.opacity})`;
    ctx.beginPath();
    ctx.arc(n.x, n.y, n.size, 0, Math.PI * 2);
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

  // Outer glow
  const glowR = finalR * (orb.hovered ? 2.8 : 2.2);
  const glow = ctx.createRadialGradient(sx, sy, finalR * 0.4, sx, sy, glowR);
  glow.addColorStop(0, hexToRgba(orb.color, orb.hovered ? 0.25 : 0.12));
  glow.addColorStop(0.6, hexToRgba(orb.color, orb.hovered ? 0.08 : 0.03));
  glow.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = glow;
  ctx.beginPath();
  ctx.arc(sx, sy, glowR, 0, Math.PI * 2);
  ctx.fill();

  // Sphere body — gradient for 3D look
  const bodyGrad = ctx.createRadialGradient(
    sx - finalR * 0.3, sy - finalR * 0.3, finalR * 0.1,
    sx, sy, finalR,
  );
  bodyGrad.addColorStop(0, hexToRgba(orb.glowColor, 0.95));
  bodyGrad.addColorStop(0.5, hexToRgba(orb.color, 0.9));
  bodyGrad.addColorStop(1, hexToRgba(orb.color, 0.7));
  ctx.fillStyle = bodyGrad;
  ctx.beginPath();
  ctx.arc(sx, sy, finalR, 0, Math.PI * 2);
  ctx.fill();

  // Specular highlight
  const specGrad = ctx.createRadialGradient(
    sx - finalR * 0.25, sy - finalR * 0.3, 0,
    sx - finalR * 0.25, sy - finalR * 0.3, finalR * 0.6,
  );
  specGrad.addColorStop(0, 'rgba(255,255,255,0.55)');
  specGrad.addColorStop(0.5, 'rgba(255,255,255,0.1)');
  specGrad.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = specGrad;
  ctx.beginPath();
  ctx.arc(sx, sy, finalR, 0, Math.PI * 2);
  ctx.fill();

  // Orbiting ring of dots (subtle)
  const dotCount = 5;
  const ringR = finalR * 1.3;
  const ringPhase = time * 0.0006 + orb.x * 0.01;
  for (let i = 0; i < dotCount; i++) {
    const angle = ringPhase + (i / dotCount) * Math.PI * 2;
    const dx = Math.cos(angle) * ringR;
    const dy = Math.sin(angle) * ringR * 0.4; // flatten for perspective
    const dotAlpha = 0.2 + 0.1 * Math.sin(time * 0.002 + i);
    ctx.fillStyle = hexToRgba(orb.color, dotAlpha);
    ctx.beginPath();
    ctx.arc(sx + dx, sy + dy, 1.5 * scale, 0, Math.PI * 2);
    ctx.fill();
  }

  // Icon emoji
  ctx.font = `${Math.round(finalR * 0.65)}px "Segoe UI Emoji", "Apple Color Emoji", sans-serif`;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(orb.domain.icon, sx, sy);

  // Label below orb
  const labelY = sy + finalR + 14 * scale;
  ctx.font = `600 ${Math.round(13 * scale)}px "Noto Serif SC", "Source Serif 4", Georgia, serif`;
  ctx.textAlign = 'center';
  ctx.fillStyle = orb.hovered ? '#1a1a1a' : 'rgba(26,26,26,0.75)';
  ctx.fillText(orb.domain.name, sx, labelY);

  // Stats line
  if (orb.stats) {
    const statsY = labelY + 14 * scale;
    ctx.font = `400 ${Math.round(10 * scale)}px "Inter", sans-serif`;
    ctx.fillStyle = 'rgba(100,100,100,0.6)';
    const parts: string[] = [];
    if (orb.stats.total_concepts != null) parts.push(`${orb.stats.total_concepts} 知识点`);
    if (orb.stats.subdomains != null) parts.push(`${orb.stats.subdomains} 子领域`);
    if (parts.length) ctx.fillText(parts.join('  ·  '), sx, statsY);
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
    () => domains.filter((d) => (d as any).is_active !== false),
    [domains],
  );

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef = useRef<number>(0);
  const bgNodesRef = useRef<BgNode[]>([]);
  const orbsRef = useRef<Orb[]>([]);
  const mouseRef = useRef<{ x: number; y: number }>({ x: -9999, y: -9999 });
  const [transitioning, setTransitioning] = useState<{ domainId: string; cx: number; cy: number; color: string } | null>(null);

  useEffect(() => { fetchDomains(); }, [fetchDomains]);

  // Init background nodes
  const initBgNodes = useCallback((w: number, h: number) => {
    const nodes: BgNode[] = [];
    for (let i = 0; i < BG_NODE_COUNT; i++) {
      nodes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        size: 1 + Math.random() * 2,
        opacity: 0.1 + Math.random() * 0.1,
      });
    }
    bgNodesRef.current = nodes;
  }, []);

  // Init orbs from domains — arrange in a loose ellipse
  useEffect(() => {
    if (activeDomains.length === 0) return;
    const count = activeDomains.length;
    const orbs: Orb[] = activeDomains.map((domain, i) => {
      const angle = (i / count) * Math.PI * 2 - Math.PI / 2;
      const rx = Math.min(320, 120 + count * 18);
      const ry = Math.min(220, 80 + count * 13);
      const jitterX = (Math.random() - 0.5) * 40;
      const jitterY = (Math.random() - 0.5) * 30;
      const stats = (domain as any).stats as { total_concepts?: number; subdomains?: number } | undefined;

      // Lighten color for glow
      const r = parseInt(domain.color.slice(1, 3), 16);
      const g = parseInt(domain.color.slice(3, 5), 16);
      const b = parseInt(domain.color.slice(5, 7), 16);
      const glowColor = `#${Math.min(255, r + 60).toString(16).padStart(2, '0')}${Math.min(255, g + 60).toString(16).padStart(2, '0')}${Math.min(255, b + 60).toString(16).padStart(2, '0')}`;

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
      for (const orb of orbs) {
        const { sx, sy, scale } = project(orb.x, orb.y, orb.z, cx, cy);
        const r = orb.radius * scale;
        const dx = mx - sx, dy = my - sy;
        orb.hovered = (dx * dx + dy * dy) < (r + 8) * (r + 8);
      }

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
        setTimeout(() => {
          navigate(`/domain/${orb.domain.id}`);
        }, TRANSITION_MS);
        return;
      }
    }
  }, [navigate, transitioning]);

  // Cursor style
  const [cursorPointer, setCursorPointer] = useState(false);
  useEffect(() => {
    const check = () => {
      const any = orbsRef.current.some((o) => o.hovered);
      setCursorPointer(any);
    };
    const id = setInterval(check, 60);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: '#e8e8e3' }}>
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
            color: '#1a1a1a',
            letterSpacing: '-0.02em',
            marginBottom: 8,
            fontFamily: '"Noto Serif SC", "Source Serif 4", Georgia, serif',
          }}
        >
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 14, color: '#888', lineHeight: 1.6 }}>
          点击星球，进入 3D 知识图谱
        </p>
      </div>

      {/* Loading state */}
      {loading && activeDomains.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin" style={{ color: '#888' }} />
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

import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { peekDomainProgress } from '@/lib/store/learning';
import { Loader } from 'lucide-react';

/* ─── Demo fallback ─── */
const DEMO_DOMAINS: import('@akg/shared').Domain[] = [
  { id: 'ai-engineering', name: 'AI编程', description: '', icon: '', color: '#8b5cf6', is_active: true, stats: { total_concepts: 400, total_edges: 615, subdomains: 15 } },
  { id: 'mathematics', name: '数学', description: '', icon: '', color: '#3b82f6', is_active: true, stats: { total_concepts: 269, total_edges: 366, subdomains: 12 } },
  { id: 'game-engine', name: '游戏引擎', description: '', icon: '', color: '#059669', is_active: true, stats: { total_concepts: 300, total_edges: 319, subdomains: 15 } },
  { id: 'game-design', name: '游戏设计', description: '', icon: '', color: '#dc2626', is_active: true, stats: { total_concepts: 250, total_edges: 274, subdomains: 12 } },
  { id: 'psychology', name: '心理学', description: '', icon: '', color: '#a855f7', is_active: true, stats: { total_concepts: 183, total_edges: 203, subdomains: 8 } },
  { id: 'physics', name: '物理', description: '', icon: '', color: '#22c55e', is_active: true, stats: { total_concepts: 194, total_edges: 232, subdomains: 10 } },
  { id: 'english', name: '英语', description: '', icon: '', color: '#eab308', is_active: true, stats: { total_concepts: 200, total_edges: 229, subdomains: 10 } },
];

const NAME_MAP: Record<string, string> = { 'ai-engineering': 'AI编程' };

/* ─── Constants ─── */
const BG = '#e8e8e4';
const TRANSITION_MS = 900;
const BASE_R = 46;           // base bubble radius
const GAP = 8;               // gap between bubbles
const DPR = typeof window !== 'undefined' ? Math.min(window.devicePixelRatio || 1, 2) : 1;

/* Fisheye lens — fixed at screen center */
const FISH_R = 350;          // influence radius from screen center
const FISH_SCALE = 1.9;      // max scale multiplier at dead center
const FISH_PUSH = 0.55;      // how much positions are pushed outward by fisheye

/* ─── Types ─── */
interface BubbleNode {
  id: string; name: string; color: string;
  concepts: number; subs: number;
  completeness: number;
  gx: number; gy: number;   // hex grid position (world coords, before fisheye)
  baseR: number;             // base radius from completeness
}

/* ─── Helpers ─── */
function completeness(c: number, e: number, s: number) {
  return c + e * 0.5 + s * 5;
}
function baseRadius(comp: number): number {
  const t = Math.max(0, Math.min(1, (comp - 300) / 500));
  return BASE_R * (0.78 + t * 0.22);
}

function hexRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

/**
 * Hex spiral: ring 0 = 1, ring 1 = 6, ring 2 = 12, ring 3 = 18 ...
 * Returns world-space {x, y} for each slot.
 */
function hexSpiralPositions(n: number, spacing: number): { x: number; y: number }[] {
  const out: { x: number; y: number }[] = [];
  if (n <= 0) return out;
  out.push({ x: 0, y: 0 });

  // Axial hex directions for pointy-top traversal
  const axialDirs: [number, number][] = [
    [1, 0], [1, -1], [0, -1], [-1, 0], [-1, 1], [0, 1],
  ];

  let ring = 1;
  while (out.length < n) {
    // Start each ring at axial (ring, 0), then walk 6 sides
    let q = ring, r = 0;
    for (let side = 0; side < 6 && out.length < n; side++) {
      for (let step = 0; step < ring && out.length < n; step++) {
        // Axial → pixel (pointy-top)
        const px = spacing * (Math.sqrt(3) * q + Math.sqrt(3) / 2 * r);
        const py = spacing * (3 / 2 * r);
        out.push({ x: px, y: py });
        q += axialDirs[(side + 2) % 6][0];
        r += axialDirs[(side + 2) % 6][1];
      }
    }
    ring++;
  }
  return out;
}

/**
 * Apply fisheye distortion to a point.
 * Lens is at (lx, ly). Points near the lens get pushed outward AND scaled up.
 * Returns { x, y, scale }.
 */
function fisheye(
  wx: number, wy: number, lx: number, ly: number,
): { x: number; y: number; scale: number } {
  const dx = wx - lx;
  const dy = wy - ly;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist < 0.5) return { x: wx, y: wy, scale: FISH_SCALE };
  if (dist > FISH_R) return { x: wx, y: wy, scale: 1 };

  // Normalized distance 0..1
  const nd = dist / FISH_R;
  // Scale: smooth falloff from FISH_SCALE at center to 1 at edge
  const scale = 1 + (FISH_SCALE - 1) * (1 - nd * nd);
  // Position push: move point outward from lens center proportional to scale
  const pushFactor = 1 + (scale - 1) * FISH_PUSH;
  const nx = lx + dx * pushFactor;
  const ny = ly + dy * pushFactor;
  return { x: nx, y: ny, scale };
}

/* ─── Draw a single bubble ─── */
function drawBubble(
  ctx: CanvasRenderingContext2D,
  b: BubbleNode, cx: number, cy: number,
  r: number, alpha: number, hovered: boolean,
) {
  if (r < 3) return;
  const [cr, cg, cb] = hexRgb(b.color);

  // Soft outer glow
  const glow = ctx.createRadialGradient(cx, cy, r * 0.5, cx, cy, r * 1.4);
  glow.addColorStop(0, `rgba(${cr},${cg},${cb},${0.15 * alpha})`);
  glow.addColorStop(1, `rgba(${cr},${cg},${cb},0)`);
  ctx.fillStyle = glow;
  ctx.beginPath(); ctx.arc(cx, cy, r * 1.4, 0, Math.PI * 2); ctx.fill();

  // Main sphere gradient
  const grad = ctx.createRadialGradient(cx - r * 0.28, cy - r * 0.3, r * 0.08, cx, cy, r);
  grad.addColorStop(0, `rgba(${Math.min(255, cr + 70)},${Math.min(255, cg + 70)},${Math.min(255, cb + 70)},${0.92 * alpha})`);
  grad.addColorStop(0.65, `rgba(${cr},${cg},${cb},${0.88 * alpha})`);
  grad.addColorStop(1, `rgba(${Math.max(0, cr - 40)},${Math.max(0, cg - 40)},${Math.max(0, cb - 40)},${0.85 * alpha})`);
  ctx.fillStyle = grad;
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();

  // Specular highlight
  const spec = ctx.createRadialGradient(cx - r * 0.22, cy - r * 0.3, 0, cx - r * 0.1, cy - r * 0.15, r * 0.52);
  spec.addColorStop(0, `rgba(255,255,255,${0.5 * alpha})`);
  spec.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = spec;
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();

  // Bottom rim light
  const rim = ctx.createRadialGradient(cx + r * 0.15, cy + r * 0.35, 0, cx, cy, r);
  rim.addColorStop(0, `rgba(255,255,255,${0.12 * alpha})`);
  rim.addColorStop(1, 'rgba(255,255,255,0)');
  ctx.fillStyle = rim;
  ctx.beginPath(); ctx.arc(cx, cy, r, 0, Math.PI * 2); ctx.fill();

  // Hover ring
  if (hovered) {
    ctx.strokeStyle = `rgba(255,255,255,${0.55 * alpha})`;
    ctx.lineWidth = 2.5;
    ctx.beginPath(); ctx.arc(cx, cy, r + 3, 0, Math.PI * 2); ctx.stroke();
  }

  // Text
  if (r < 16) return;
  const fontSize = Math.max(9, Math.round(r * 0.3));
  const subSize = Math.max(7, Math.round(r * 0.19));
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = `600 ${fontSize}px "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif`;
  ctx.fillStyle = `rgba(255,255,255,${0.95 * alpha})`;
  const hasSubline = r > 28;
  ctx.fillText(b.name, cx, hasSubline ? cy - subSize * 0.45 : cy, r * 1.7);

  if (hasSubline) {
    const info: string[] = [];
    if (b.concepts) info.push(b.concepts + ' \u77e5\u8bc6\u70b9');
    if (b.subs) info.push(b.subs + ' \u5b50\u9886\u57df');
    if (info.length) {
      ctx.font = `400 ${subSize}px "Microsoft YaHei","PingFang SC",system-ui,sans-serif`;
      ctx.fillStyle = `rgba(255,255,255,${0.6 * alpha})`;
      ctx.fillText(info.join(' \u00b7 '), cx, cy + fontSize * 0.55, r * 1.7);
    }
  }
}

/* ═══════════════════════════════════════════
   HomePage — Apple Watch honeycomb + fisheye
   ═══════════════════════════════════════════ */
export function HomePage() {
  const nav = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const active = domains.filter(d => d.is_active !== false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [trans, setTrans] = useState<{ id: string; cx: number; cy: number; color: string } | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);
  const navRef = useRef(nav); navRef.current = nav;

  useEffect(() => {
    fetchDomains().then(() => {
      if (useDomainStore.getState().domains.length === 0)
        useDomainStore.setState({ domains: DEMO_DOMAINS, loading: false, error: null });
    });
  }, [fetchDomains]);

  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; if (timerRef.current) clearTimeout(timerRef.current); };
  }, []);

  /* ─── Build hex grid bubble data ─── */
  const bubbles = useMemo<BubbleNode[]>(() => {
    if (!active.length) return [];
    const items = active.map(d => {
      const c = d.stats?.total_concepts ?? 0, e = d.stats?.total_edges ?? 0, s = d.stats?.subdomains ?? 0;
      return { id: d.id, name: NAME_MAP[d.id] || d.name, color: d.color, concepts: c, subs: s, completeness: completeness(c, e, s) };
    });
    items.sort((a, b) => b.completeness - a.completeness);
    const spacing = BASE_R + GAP;
    const positions = hexSpiralPositions(items.length, spacing);
    return items.map((it, i) => ({
      ...it,
      gx: positions[i].x,
      gy: positions[i].y,
      baseR: baseRadius(it.completeness),
    }));
  }, [active]);

  /* ─── Interaction + render state ─── */
  const stateRef = useRef({
    offsetX: 0, offsetY: 0,
    velX: 0, velY: 0,
    dragStartX: 0, dragStartY: 0,
    dragOffsetX: 0, dragOffsetY: 0,
    lastMoveTime: 0,
    lastMoveX: 0, lastMoveY: 0,
    dragging: false,
    mouseX: -9999, mouseY: -9999,
  });

  /* ─── Canvas loop ─── */
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !bubbles.length) return;
    const ctx = canvas.getContext('2d')!;
    let raf = 0;
    let dead = false;
    const s = stateRef.current;

    const resize = () => {
      const rect = canvas.parentElement!.getBoundingClientRect();
      canvas.width = rect.width * DPR;
      canvas.height = rect.height * DPR;
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(canvas.parentElement!);

    /* ── Pointer events ── */
    const onDown = (e: PointerEvent) => {
      s.dragging = true;
      s.dragStartX = e.clientX; s.dragStartY = e.clientY;
      s.dragOffsetX = s.offsetX; s.dragOffsetY = s.offsetY;
      s.velX = 0; s.velY = 0;
      s.lastMoveX = e.clientX; s.lastMoveY = e.clientY;
      s.lastMoveTime = performance.now();
      canvas.setPointerCapture(e.pointerId);
    };
    const onMove = (e: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      s.mouseX = e.clientX - rect.left;
      s.mouseY = e.clientY - rect.top;
      if (s.dragging) {
        s.offsetX = s.dragOffsetX + (e.clientX - s.dragStartX);
        s.offsetY = s.dragOffsetY + (e.clientY - s.dragStartY);
        const now = performance.now();
        const dt = now - s.lastMoveTime;
        if (dt > 0) {
          s.velX = (e.clientX - s.lastMoveX) / dt * 16;
          s.velY = (e.clientY - s.lastMoveY) / dt * 16;
        }
        s.lastMoveX = e.clientX; s.lastMoveY = e.clientY;
        s.lastMoveTime = now;
      }
    };
    const onUp = (e: PointerEvent) => {
      const wasDrag = Math.abs(e.clientX - s.dragStartX) > 5 || Math.abs(e.clientY - s.dragStartY) > 5;
      s.dragging = false;
      canvas.releasePointerCapture(e.pointerId);
      if (!wasDrag) {
        // Click — find hit bubble based on fisheye-transformed positions
        const W = canvas.width / DPR, H = canvas.height / DPR;
        const lx = W / 2, ly = H / 2;
        for (let i = bubbles.length - 1; i >= 0; i--) {
          const b = bubbles[i];
          const wx = lx + s.offsetX + b.gx;
          const wy = ly + s.offsetY + b.gy;
          const f = fisheye(wx, wy, lx, ly);
          const r = b.baseR * f.scale;
          const dx = s.mouseX - f.x, dy = s.mouseY - f.y;
          if (dx * dx + dy * dy <= r * r) {
            const rect = canvas.getBoundingClientRect();
            setTrans({ id: b.id, cx: rect.left + f.x, cy: rect.top + f.y, color: b.color });
            timerRef.current = setTimeout(() => {
              if (alive.current) navRef.current('/domain/' + b.id);
            }, TRANSITION_MS);
            break;
          }
        }
      }
    };
    const onLeave = () => { s.mouseX = -9999; s.mouseY = -9999; };

    canvas.addEventListener('pointerdown', onDown);
    canvas.addEventListener('pointermove', onMove);
    canvas.addEventListener('pointerup', onUp);
    canvas.addEventListener('pointerleave', onLeave);

    /* ── Render loop ── */
    const frame = () => {
      if (dead) return;
      const W = canvas.width / DPR;
      const H = canvas.height / DPR;

      // Inertia when not dragging
      if (!s.dragging) {
        s.offsetX += s.velX;
        s.offsetY += s.velY;
        s.velX *= 0.94;
        s.velY *= 0.94;
        if (Math.abs(s.velX) < 0.05) s.velX = 0;
        if (Math.abs(s.velY) < 0.05) s.velY = 0;
      }

      // Lens center = screen center
      const lx = W / 2, ly = H / 2;

      // Clear
      ctx.save();
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      ctx.fillStyle = BG;
      ctx.fillRect(0, 0, W, H);

      // Hit test for hover cursor
      let hoveredIdx = -1;
      for (let i = bubbles.length - 1; i >= 0; i--) {
        const b = bubbles[i];
        const wx = lx + s.offsetX + b.gx;
        const wy = ly + s.offsetY + b.gy;
        const f = fisheye(wx, wy, lx, ly);
        const r = b.baseR * f.scale;
        const dx = s.mouseX - f.x, dy = s.mouseY - f.y;
        if (dx * dx + dy * dy <= r * r) { hoveredIdx = i; break; }
      }
      canvas.style.cursor = s.dragging ? 'grabbing' : hoveredIdx >= 0 ? 'pointer' : 'grab';

      // Collect draw data so we can sort back-to-front by scale (small first, big on top)
      const drawList: { b: BubbleNode; fx: number; fy: number; r: number; scale: number; idx: number }[] = [];
      for (let i = 0; i < bubbles.length; i++) {
        const b = bubbles[i];
        const wx = lx + s.offsetX + b.gx;
        const wy = ly + s.offsetY + b.gy;
        // Cull off-screen
        if (wx < -150 || wx > W + 150 || wy < -150 || wy > H + 150) continue;
        const f = fisheye(wx, wy, lx, ly);
        drawList.push({ b, fx: f.x, fy: f.y, r: b.baseR * f.scale, scale: f.scale, idx: i });
      }
      drawList.sort((a, b) => a.scale - b.scale);

      // Draw
      for (const d of drawList) {
        const alpha = Math.max(0.35, Math.min(1, 0.35 + (d.scale - 1) * 0.72));
        drawBubble(ctx, d.b, d.fx, d.fy, d.r, alpha, d.idx === hoveredIdx);
      }

      ctx.restore();
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);

    return () => {
      dead = true;
      cancelAnimationFrame(raf);
      ro.disconnect();
      canvas.removeEventListener('pointerdown', onDown);
      canvas.removeEventListener('pointermove', onMove);
      canvas.removeEventListener('pointerup', onUp);
      canvas.removeEventListener('pointerleave', onLeave);
    };
  }, [bubbles]);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: BG }}>
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" style={{ touchAction: 'none' }} />
      {/* Header */}
      <div className="absolute left-0 right-0 text-center pointer-events-none select-none" style={{ top: 28, zIndex: 10 }}>
        <h1 style={{ fontSize: 26, fontWeight: 500, color: '#2a2a2a', letterSpacing: '-0.02em', marginBottom: 6, fontFamily: '"Noto Serif SC","Source Serif 4",Georgia,serif', textShadow: '0 1px 8px rgba(232,232,228,0.9)' }}>
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 13, color: '#888', lineHeight: 1.6, textShadow: '0 1px 6px rgba(232,232,228,0.8)' }}>
          拖拽平移 · 点击进入 3D 知识图谱
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

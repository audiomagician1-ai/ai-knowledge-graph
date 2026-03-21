import { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { Loader } from 'lucide-react';

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

const NAME_MAP: Record<string, string> = { 'ai-engineering': 'AI编程' };

/* ─── Constants ─── */
const BG = '#e8e8e4';
const TRANSITION_MS = 900;
const BASE_R = 44;
const CELL = BASE_R * 2 + 10; // hex cell center-to-center distance
const DPR = typeof window !== 'undefined' ? Math.min(window.devicePixelRatio || 1, 2) : 1;

/* Fisheye — only scales size, does NOT move positions */
const FISH_R = 320;
const FISH_MAX = 1.65;
const FISH_MIN = 0.55;

/* ─── Types ─── */
interface BubbleNode {
  id: string; name: string; color: string;
  concepts: number; subs: number;
  gx: number; gy: number;
  baseR: number;
}

/* ─── Helpers ─── */
function completeness(c: number, e: number, s: number) { return c + e * 0.5 + s * 5; }

function hexRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

/** Axial hex spiral positions */
function hexSpiral(n: number, spacing: number): { x: number; y: number }[] {
  const out: { x: number; y: number }[] = [];
  if (n <= 0) return out;
  out.push({ x: 0, y: 0 });
  const dirs: [number, number][] = [[1,0],[1,-1],[0,-1],[-1,0],[-1,1],[0,1]];
  let ring = 1;
  while (out.length < n) {
    let q = ring, r = 0;
    for (let side = 0; side < 6 && out.length < n; side++) {
      for (let step = 0; step < ring && out.length < n; step++) {
        const px = spacing * (Math.sqrt(3) * q + Math.sqrt(3) / 2 * r);
        const py = spacing * (1.5 * r);
        out.push({ x: px, y: py });
        q += dirs[(side + 2) % 6][0];
        r += dirs[(side + 2) % 6][1];
      }
    }
    ring++;
  }
  return out;
}

/** Fisheye scale factor based on distance from screen center. Only affects size. */
function fishScale(dist: number): number {
  if (dist >= FISH_R) return FISH_MIN;
  const nd = dist / FISH_R;
  // Smooth: cubic ease-out from FISH_MAX at center to FISH_MIN at edge
  const t = 1 - nd * nd;
  return FISH_MIN + (FISH_MAX - FISH_MIN) * t;
}

/* ─── Flat bubble drawing ─── */
function drawBubble(
  ctx: CanvasRenderingContext2D,
  b: BubbleNode, cx: number, cy: number,
  r: number, scale: number, hovered: boolean,
) {
  if (r < 2) return;
  const [cr, cg, cb] = hexRgb(b.color);
  const alpha = Math.max(0.3, Math.min(1, (scale - FISH_MIN) / (FISH_MAX - FISH_MIN)));

  // Drop shadow
  ctx.save();
  ctx.shadowColor = `rgba(${cr},${cg},${cb},${0.3 * alpha})`;
  ctx.shadowBlur = r * 0.3;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = r * 0.08;

  // Flat filled circle with subtle gradient
  const grad = ctx.createRadialGradient(cx - r * 0.2, cy - r * 0.2, 0, cx, cy, r);
  grad.addColorStop(0, `rgba(${Math.min(255, cr + 40)},${Math.min(255, cg + 40)},${Math.min(255, cb + 40)},${alpha})`);
  grad.addColorStop(1, `rgba(${cr},${cg},${cb},${alpha})`);
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // Hover ring
  if (hovered) {
    ctx.strokeStyle = `rgba(${cr},${cg},${cb},0.8)`;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(cx, cy, r + 2, 0, Math.PI * 2);
    ctx.stroke();
  }

  // Text — only if big enough
  if (r < 14) return;
  const fontSize = Math.max(10, Math.round(r * 0.3));
  const subSize = Math.max(8, Math.round(r * 0.2));
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = `600 ${fontSize}px "Microsoft YaHei","PingFang SC","Noto Sans SC",system-ui,sans-serif`;
  ctx.fillStyle = `rgba(255,255,255,${0.95 * alpha})`;
  const showSub = r > 26;
  ctx.fillText(b.name, cx, showSub ? cy - subSize * 0.5 : cy, r * 1.8);

  if (showSub) {
    const parts: string[] = [];
    if (b.concepts) parts.push(b.concepts + ' \u77e5\u8bc6\u70b9');
    if (b.subs) parts.push(b.subs + ' \u5b50\u9886\u57df');
    if (parts.length) {
      ctx.font = `400 ${subSize}px "Microsoft YaHei","PingFang SC",system-ui,sans-serif`;
      ctx.fillStyle = `rgba(255,255,255,${0.6 * alpha})`;
      ctx.fillText(parts.join(' \u00b7 '), cx, cy + fontSize * 0.6, r * 1.8);
    }
  }
}

/* ═══════════════════════════════════════════════
   HomePage — Honeycomb grid + center fisheye
   Infinite drag wrapping, flat style
   ═══════════════════════════════════════════════ */
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

  /* ─── Build hex bubble data ─── */
  const bubbles = useMemo<BubbleNode[]>(() => {
    if (!active.length) return [];
    const items = active.map(d => {
      const c = d.stats?.total_concepts ?? 0, e = d.stats?.total_edges ?? 0, s = d.stats?.subdomains ?? 0;
      return { id: d.id, name: NAME_MAP[d.id] || d.name, color: d.color, concepts: c, subs: s, comp: completeness(c, e, s) };
    });
    items.sort((a, b) => b.comp - a.comp);
    const positions = hexSpiral(items.length, CELL);
    return items.map((it, i) => {
      const t = Math.max(0, Math.min(1, (it.comp - 300) / 500));
      return { ...it, gx: positions[i].x, gy: positions[i].y, baseR: BASE_R * (0.8 + t * 0.2) };
    });
  }, [active]);

  /* ─── Compute bounding box for wrap ─── */
  const bbox = useMemo(() => {
    if (!bubbles.length) return { w: 0, h: 0 };
    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const b of bubbles) {
      if (b.gx - BASE_R < minX) minX = b.gx - BASE_R;
      if (b.gx + BASE_R > maxX) maxX = b.gx + BASE_R;
      if (b.gy - BASE_R < minY) minY = b.gy - BASE_R;
      if (b.gy + BASE_R > maxY) maxY = b.gy + BASE_R;
    }
    return { w: maxX - minX + CELL, h: maxY - minY + CELL };
  }, [bubbles]);

  /* ─── State ref ─── */
  const st = useRef({
    ox: 0, oy: 0,
    vx: 0, vy: 0,
    dsx: 0, dsy: 0, dox: 0, doy: 0,
    ltm: 0, lmx: 0, lmy: 0,
    dragging: false,
    mx: -9999, my: -9999,
  });

  /* ─── Canvas loop ─── */
  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs || !bubbles.length) return;
    const ctx = cvs.getContext('2d')!;
    let raf = 0, dead = false;
    const s = st.current;

    const resize = () => {
      const r = cvs.parentElement!.getBoundingClientRect();
      cvs.width = r.width * DPR;
      cvs.height = r.height * DPR;
      cvs.style.width = r.width + 'px';
      cvs.style.height = r.height + 'px';
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(cvs.parentElement!);

    const onDown = (e: PointerEvent) => {
      s.dragging = true; s.dsx = e.clientX; s.dsy = e.clientY;
      s.dox = s.ox; s.doy = s.oy; s.vx = 0; s.vy = 0;
      s.lmx = e.clientX; s.lmy = e.clientY; s.ltm = performance.now();
      cvs.setPointerCapture(e.pointerId);
    };
    const onMove = (e: PointerEvent) => {
      const r = cvs.getBoundingClientRect();
      s.mx = e.clientX - r.left; s.my = e.clientY - r.top;
      if (s.dragging) {
        s.ox = s.dox + (e.clientX - s.dsx);
        s.oy = s.doy + (e.clientY - s.dsy);
        const now = performance.now(), dt = now - s.ltm;
        if (dt > 0) { s.vx = (e.clientX - s.lmx) / dt * 16; s.vy = (e.clientY - s.lmy) / dt * 16; }
        s.lmx = e.clientX; s.lmy = e.clientY; s.ltm = now;
      }
    };
    const onUp = (e: PointerEvent) => {
      const wasDrag = Math.abs(e.clientX - s.dsx) > 5 || Math.abs(e.clientY - s.dsy) > 5;
      s.dragging = false; cvs.releasePointerCapture(e.pointerId);
      if (!wasDrag) {
        const W = cvs.width / DPR, H = cvs.height / DPR;
        const cx = W / 2, cy = H / 2;
        // Reverse hit-test with wrapping
        for (let i = bubbles.length - 1; i >= 0; i--) {
          const b = bubbles[i];
          let wx = cx + s.ox + b.gx, wy = cy + s.oy + b.gy;
          if (bbox.w > 0) { wx = ((wx % bbox.w) + bbox.w) % bbox.w; if (wx > W + BASE_R * 2) wx -= bbox.w; }
          if (bbox.h > 0) { wy = ((wy % bbox.h) + bbox.h) % bbox.h; if (wy > H + BASE_R * 2) wy -= bbox.h; }
          const dist = Math.sqrt((wx - cx) * (wx - cx) + (wy - cy) * (wy - cy));
          const sc = fishScale(dist);
          const r = b.baseR * sc;
          const dx = s.mx - wx, dy = s.my - wy;
          if (dx * dx + dy * dy <= r * r) {
            const rect = cvs.getBoundingClientRect();
            setTrans({ id: b.id, cx: rect.left + wx, cy: rect.top + wy, color: b.color });
            timerRef.current = setTimeout(() => { if (alive.current) navRef.current('/domain/' + b.id); }, TRANSITION_MS);
            break;
          }
        }
      }
    };
    const onLeave = () => { s.mx = -9999; s.my = -9999; };

    cvs.addEventListener('pointerdown', onDown);
    cvs.addEventListener('pointermove', onMove);
    cvs.addEventListener('pointerup', onUp);
    cvs.addEventListener('pointerleave', onLeave);

    const frame = () => {
      if (dead) return;
      const W = cvs.width / DPR, H = cvs.height / DPR;

      // Inertia
      if (!s.dragging) {
        s.ox += s.vx; s.oy += s.vy;
        s.vx *= 0.94; s.vy *= 0.94;
        if (Math.abs(s.vx) < 0.05) s.vx = 0;
        if (Math.abs(s.vy) < 0.05) s.vy = 0;
      }

      const cx = W / 2, cy = H / 2;

      ctx.save();
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      ctx.fillStyle = BG;
      ctx.fillRect(0, 0, W, H);

      // Build draw list with wrapping
      type DI = { b: BubbleNode; x: number; y: number; r: number; sc: number; idx: number };
      const drawList: DI[] = [];

      for (let i = 0; i < bubbles.length; i++) {
        const b = bubbles[i];
        let wx = cx + s.ox + b.gx;
        let wy = cy + s.oy + b.gy;

        // Wrap for infinite scrolling
        if (bbox.w > 0) {
          wx = ((wx % bbox.w) + bbox.w) % bbox.w;
          if (wx > W + BASE_R * 2) wx -= bbox.w;
        }
        if (bbox.h > 0) {
          wy = ((wy % bbox.h) + bbox.h) % bbox.h;
          if (wy > H + BASE_R * 2) wy -= bbox.h;
        }

        // Cull
        if (wx < -BASE_R * 2 || wx > W + BASE_R * 2 || wy < -BASE_R * 2 || wy > H + BASE_R * 2) continue;

        const dist = Math.sqrt((wx - cx) * (wx - cx) + (wy - cy) * (wy - cy));
        const sc = fishScale(dist);
        drawList.push({ b, x: wx, y: wy, r: b.baseR * sc, sc, idx: i });
      }

      // Sort: small (far) first, big (near center) on top
      drawList.sort((a, b) => a.sc - b.sc);

      // Hover detect
      let hovIdx = -1;
      for (let i = drawList.length - 1; i >= 0; i--) {
        const d = drawList[i];
        const dx = s.mx - d.x, dy = s.my - d.y;
        if (dx * dx + dy * dy <= d.r * d.r) { hovIdx = d.idx; break; }
      }
      cvs.style.cursor = s.dragging ? 'grabbing' : hovIdx >= 0 ? 'pointer' : 'grab';

      // Draw
      for (const d of drawList) {
        drawBubble(ctx, d.b, d.x, d.y, d.r, d.sc, d.idx === hovIdx);
      }

      ctx.restore();
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);

    return () => {
      dead = true; cancelAnimationFrame(raf); ro.disconnect();
      cvs.removeEventListener('pointerdown', onDown);
      cvs.removeEventListener('pointermove', onMove);
      cvs.removeEventListener('pointerup', onUp);
      cvs.removeEventListener('pointerleave', onLeave);
    };
  }, [bubbles, bbox]);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: BG }}>
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" style={{ touchAction: 'none' }} />
      {/* Header */}
      <div className="absolute left-0 right-0 text-center pointer-events-none select-none" style={{ top: 28, zIndex: 10 }}>
        <h1 style={{ fontSize: 26, fontWeight: 500, color: '#2a2a2a', letterSpacing: '-0.02em', marginBottom: 6, fontFamily: '"Noto Serif SC","Source Serif 4",Georgia,serif', textShadow: '0 1px 8px rgba(232,232,228,0.9)' }}>
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 13, color: '#888', lineHeight: 1.6, textShadow: '0 1px 6px rgba(232,232,228,0.8)' }}>
          拖拽平移 \u00b7 点击进入 3D 知识图谱
        </p>
      </div>
      {loading && active.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin" style={{ color: '#888' }} />
        </div>
      )}
      {trans && (
        <div className="fixed inset-0" style={{ zIndex: 50, pointerEvents: 'none' }}>
          <div style={{ position: 'absolute', left: trans.cx, top: trans.cy, width: 0, height: 0, borderRadius: '50%', backgroundColor: trans.color, transform: 'translate(-50%,-50%)', animation: 'orb-expand ' + TRANSITION_MS + 'ms cubic-bezier(0.4,0,0.2,1) forwards', opacity: 0.85 }} />
        </div>
      )}
      <style>{`@keyframes orb-expand { 0% { width:0;height:0;opacity:0.9 } 100% { width:300vmax;height:300vmax;opacity:0.4 } }`}</style>
    </div>
  );
}

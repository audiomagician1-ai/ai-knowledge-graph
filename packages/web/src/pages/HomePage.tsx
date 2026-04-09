import { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { Loader, BarChart3, Trophy, Settings as SettingsIcon, StickyNote, Users, History, Map, FileText, Bell } from 'lucide-react';
import { WelcomeGuide } from '@/components/common/WelcomeGuide';
import { ReviewBanner } from '@/components/common/ReviewBanner';
import { DailyRecommendation } from '@/components/common/DailyRecommendation';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import {
  DEMO_DOMAINS, NAME_MAP, BG, TRANSITION_MS, DPR,
  BASE_R, HEX_SPACING, FISH_MAX, FISH_MIN, FISH_POWER, FISH_PUSH, FISH_R_FACTOR,
  INITIAL_PAN_Y, FRICTION, VEL_THRESHOLD, VEL_CAP,
  TAP_THRESHOLD_DESKTOP, TAP_THRESHOLD_MOBILE, TAP_HIT_PADDING_MOBILE,
  completeness, buildRectHexGrid, drawBubble,
  type DomainItem,
} from '@/lib/utils/home-canvas-utils';

export function HomePage() {
  const nav = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const active = domains.filter(d => d.is_active !== false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [trans, setTrans] = useState<{ id: string; cx: number; cy: number; color: string } | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);
  const navRef = useRef(nav); navRef.current = nav;

  useKeyboardShortcuts([
    { key: 'd', handler: () => nav('/dashboard'), description: 'Go to dashboard' },
    { key: 'g', handler: () => nav('/graph'), description: 'Go to 3D graph' },
    { key: 's', handler: () => nav('/settings'), description: 'Go to settings' },
    { key: '?', shift: true, handler: () => nav('/dashboard'), description: 'Help / Dashboard' },
  ]);

  const isMobile = useMemo(() => typeof window !== 'undefined' && window.innerWidth < 768, []);
  const mScale = isMobile ? 0.55 : 1;
  const baseR = BASE_R * mScale;
  const hexSpacing = HEX_SPACING * mScale;

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

  const sorted = useMemo<DomainItem[]>(() => {
    if (!active.length) return [];
    const items = active.map(d => {
      const c = d.stats?.total_concepts ?? 0, e = d.stats?.total_edges ?? 0, s = d.stats?.subdomains ?? 0;
      const hashSeed = d.id.split('').reduce((a, ch) => a + ch.charCodeAt(0), 0);
      const learners = Math.max(12, Math.round(c * 0.6 + (hashSeed % 80) + 15));
      return { id: d.id, name: NAME_MAP[d.id] || d.name, color: d.color, concepts: c, subs: s, comp: completeness(c, e, s), learners };
    });
    items.sort((a, b) => b.comp - a.comp);
    return items;
  }, [active]);

  const N = sorted.length;
  const gridData = useMemo(() => buildRectHexGrid(N, hexSpacing), [N, hexSpacing]);
  const hexGrid = gridData.positions;
  const totalSlots = gridData.totalSlots;
  const wrapW = gridData.wrapW;
  const wrapH = gridData.wrapH;

  const st = useRef({
    panX: 0, panY: INITIAL_PAN_Y, velX: 0, velY: 0,
    dragging: false, dragStartX: 0, dragStartY: 0,
    dragStartPanX: 0, dragStartPanY: 0,
    lastX: 0, lastY: 0, lastT: 0, mx: -9999, my: -9999,
  });

  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs || N === 0) return;
    const ctx = cvs.getContext('2d')!;
    let raf = 0, dead = false;
    const s = st.current;
    const _baseR = baseR;

    const resize = () => {
      const r = cvs.parentElement!.getBoundingClientRect();
      cvs.width = r.width * DPR; cvs.height = r.height * DPR;
      cvs.style.width = r.width + 'px'; cvs.style.height = r.height + 'px';
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(cvs.parentElement!);

    const onDown = (e: PointerEvent) => {
      s.dragging = true; s.velX = 0; s.velY = 0;
      s.dragStartX = e.clientX; s.dragStartY = e.clientY;
      s.dragStartPanX = s.panX; s.dragStartPanY = s.panY;
      s.lastX = e.clientX; s.lastY = e.clientY; s.lastT = performance.now();
      const rect = cvs.getBoundingClientRect();
      s.mx = e.clientX - rect.left; s.my = e.clientY - rect.top;
      cvs.setPointerCapture(e.pointerId);
    };
    const onMove = (e: PointerEvent) => {
      const rect = cvs.getBoundingClientRect();
      s.mx = e.clientX - rect.left; s.my = e.clientY - rect.top;
      if (!s.dragging) return;
      s.panX = s.dragStartPanX + (e.clientX - s.dragStartX);
      s.panY = s.dragStartPanY + (e.clientY - s.dragStartY);
      const now = performance.now(); const dt = now - s.lastT;
      if (dt > 0) { s.velX = (e.clientX - s.lastX) / dt * 16; s.velY = (e.clientY - s.lastY) / dt * 16; }
      s.lastX = e.clientX; s.lastY = e.clientY; s.lastT = now;
    };
    const onUp = (e: PointerEvent) => {
      const tapThreshold = e.pointerType === 'touch' ? TAP_THRESHOLD_MOBILE : TAP_THRESHOLD_DESKTOP;
      const wasDrag = Math.abs(e.clientX - s.dragStartX) > tapThreshold || Math.abs(e.clientY - s.dragStartY) > tapThreshold;
      s.dragging = false; cvs.releasePointerCapture(e.pointerId);
      const vLen = Math.sqrt(s.velX * s.velX + s.velY * s.velY);
      if (vLen > VEL_CAP) { const sc = VEL_CAP / vLen; s.velX *= sc; s.velY *= sc; }
      if (!wasDrag) {
        const rect = cvs.getBoundingClientRect();
        const tapX = e.clientX - rect.left; const tapY = e.clientY - rect.top;
        const W = cvs.width / DPR, H = cvs.height / DPR;
        const centerX = W / 2, centerY = H / 2;
        const fishR = Math.min(W, H) * FISH_R_FACTOR;
        const hits: { idx: number; sx: number; sy: number; sr: number }[] = [];
        for (let i = 0; i < totalSlots; i++) {
          const bx = hexGrid[i].x + s.panX, by = hexGrid[i].y + s.panY;
          let bestDx = bx, bestDy = by;
          for (const ox of [-wrapW, 0, wrapW]) {
            for (const oy of [-wrapH, 0, wrapH]) {
              const cx = bx + ox, cy = by + oy;
              if (cx * cx + cy * cy < bestDx * bestDx + bestDy * bestDy) { bestDx = cx; bestDy = cy; }
            }
          }
          const sd = Math.sqrt(bestDx * bestDx + bestDy * bestDy);
          const t = Math.max(0, 1 - sd / fishR);
          if (t <= 0) continue;
          const curve = Math.pow(t, FISH_POWER);
          const scale = FISH_MIN + (FISH_MAX - FISH_MIN) * curve;
          const push = 1 + curve * FISH_PUSH;
          hits.push({ idx: i, sx: centerX + bestDx * push, sy: centerY + bestDy * push, sr: _baseR * scale });
        }
        hits.sort((a, b) => b.sr - a.sr);
        const hitPad = e.pointerType === 'touch' ? TAP_HIT_PADDING_MOBILE : 0;
        for (const h of hits) {
          const dx = tapX - h.sx, dy = tapY - h.sy;
          if (dx * dx + dy * dy <= (h.sr + hitPad) ** 2) {
            const d = sorted[h.idx % N];
            setTrans({ id: d.id, cx: rect.left + h.sx, cy: rect.top + h.sy, color: d.color });
            timerRef.current = setTimeout(() => { if (alive.current) navRef.current('/domain/' + d.id); }, TRANSITION_MS);
            return;
          }
        }
      }
    };
    const onLeave = (e: PointerEvent) => { if (e.pointerType === 'touch') return; s.mx = -9999; s.my = -9999; };
    cvs.addEventListener('pointerdown', onDown);
    cvs.addEventListener('pointermove', onMove);
    cvs.addEventListener('pointerup', onUp);
    cvs.addEventListener('pointerleave', onLeave);

    const frame = () => {
      if (dead) return;
      const W = cvs.width / DPR, H = cvs.height / DPR;
      const centerX = W / 2, centerY = H / 2;
      const fishR = Math.min(W, H) * FISH_R_FACTOR;
      if (!s.dragging) {
        if (Math.abs(s.velX) > VEL_THRESHOLD || Math.abs(s.velY) > VEL_THRESHOLD) {
          s.panX += s.velX; s.panY += s.velY; s.velX *= FRICTION; s.velY *= FRICTION;
        } else { s.velX = 0; s.velY = 0; }
      }
      s.panX = ((s.panX % wrapW) + wrapW) % wrapW;
      s.panY = ((s.panY % wrapH) + wrapH) % wrapH;

      ctx.save(); ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      ctx.fillStyle = BG; ctx.fillRect(0, 0, W, H);
      ctx.save(); ctx.beginPath(); ctx.arc(centerX, centerY, fishR * 1.05, 0, Math.PI * 2); ctx.clip();

      interface DrawItem { idx: number; sx: number; sy: number; sr: number; alpha: number; screenDist: number }
      const drawItems: DrawItem[] = [];
      for (let i = 0; i < totalSlots; i++) {
        const baseX = hexGrid[i].x + s.panX, baseY = hexGrid[i].y + s.panY;
        let bestDx = baseX, bestDy = baseY;
        for (const ox of [-wrapW, 0, wrapW]) {
          for (const oy of [-wrapH, 0, wrapH]) {
            const cx = baseX + ox, cy = baseY + oy;
            if (cx * cx + cy * cy < bestDx * bestDx + bestDy * bestDy) { bestDx = cx; bestDy = cy; }
          }
        }
        const screenDist = Math.sqrt(bestDx * bestDx + bestDy * bestDy);
        const t = Math.max(0, 1 - screenDist / fishR);
        if (t <= 0) continue;
        const curve = Math.pow(t, FISH_POWER);
        const scale = FISH_MIN + (FISH_MAX - FISH_MIN) * curve;
        const push = 1 + curve * FISH_PUSH;
        const sx = centerX + bestDx * push, sy = centerY + bestDy * push;
        const sr = _baseR * scale;
        const alpha = Math.pow(t, 3.0);
        if (sx + sr < -20 || sx - sr > W + 20 || sy + sr < -20 || sy - sr > H + 20) continue;
        if (alpha < 0.02) continue;
        drawItems.push({ idx: i, sx, sy, sr, alpha, screenDist });
      }
      drawItems.sort((a, b) => b.screenDist - a.screenDist);

      let hovIdx = -1;
      for (let i = drawItems.length - 1; i >= 0; i--) {
        const d = drawItems[i];
        const dx = s.mx - d.sx, dy = s.my - d.sy;
        if (dx * dx + dy * dy <= d.sr * d.sr) { hovIdx = d.idx; break; }
      }
      cvs.style.cursor = s.dragging ? 'grabbing' : hovIdx >= 0 ? 'pointer' : 'grab';
      for (const d of drawItems) {
        const dd = sorted[d.idx % N];
        drawBubble(ctx, dd.name, dd.color, dd.concepts, dd.subs, d.sx, d.sy, d.sr, d.alpha, d.idx === hovIdx, dd.learners);
      }
      ctx.restore();

      const vigInner = fishR * 0.40, vigOuter = fishR * 1.05;
      const vigGrad = ctx.createRadialGradient(centerX, centerY, vigInner, centerX, centerY, vigOuter);
      vigGrad.addColorStop(0, 'rgba(240,240,236,0)'); vigGrad.addColorStop(0.25, 'rgba(240,240,236,0)');
      vigGrad.addColorStop(0.5, 'rgba(240,240,236,0.25)'); vigGrad.addColorStop(0.7, 'rgba(240,240,236,0.65)');
      vigGrad.addColorStop(0.85, 'rgba(240,240,236,0.92)'); vigGrad.addColorStop(1, BG);
      ctx.fillStyle = vigGrad; ctx.fillRect(0, 0, W, H);
      ctx.restore();
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);
    return () => { dead = true; cancelAnimationFrame(raf); ro.disconnect(); cvs.removeEventListener('pointerdown', onDown); cvs.removeEventListener('pointermove', onMove); cvs.removeEventListener('pointerup', onUp); cvs.removeEventListener('pointerleave', onLeave); };
  }, [sorted, N, hexGrid, totalSlots, wrapW, wrapH, gridData, baseR]);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: BG }}>
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" style={{ touchAction: 'none' }} />
      <div className="absolute left-0 right-0 text-center pointer-events-none select-none" style={{ top: 32, zIndex: 10 }}>
        <h1 style={{ fontSize: 20, fontWeight: 600, color: '#1a1a1a', letterSpacing: '0.04em', marginBottom: 6, fontFamily: '-apple-system,"SF Pro Display","Helvetica Neue","PingFang SC",sans-serif', textShadow: '0 1px 12px rgba(240,240,236,0.95)' }}>
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 12, color: '#999', letterSpacing: '0.06em', fontFamily: '-apple-system,"SF Pro Text","PingFang SC",sans-serif', textShadow: '0 1px 8px rgba(240,240,236,0.9)' }}>
          拖动浏览 · 点击进入 3D 知识图谱
        </p>
      </div>
      {loading && active.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin" style={{ color: '#888' }} />
        </div>
      )}
      <ReviewBanner />
      <DailyRecommendation />
      <WelcomeGuide />
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 pointer-events-auto" style={{ zIndex: 15 }}>
        <div className="flex items-center gap-2 px-3 py-2 rounded-2xl" style={{ backgroundColor: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(16px)', boxShadow: '0 4px 24px rgba(0,0,0,0.08)', border: '1px solid rgba(0,0,0,0.06)' }}>
          <QuickNavBtn icon={<BarChart3 size={18} />} label="分析" onClick={() => nav('/dashboard')} />
          <QuickNavBtn icon={<Trophy size={18} />} label="排行" onClick={() => nav('/leaderboard')} />
          <QuickNavBtn icon={<StickyNote size={18} />} label="笔记" onClick={() => nav('/notes')} />
          <QuickNavBtn icon={<History size={18} />} label="历史" onClick={() => nav('/history')} />
          <QuickNavBtn icon={<Map size={18} />} label="旅程" onClick={() => nav('/journey')} />
          <QuickNavBtn icon={<FileText size={18} />} label="报告" onClick={() => nav('/report')} />
          <QuickNavBtn icon={<Bell size={18} />} label="通知" onClick={() => nav('/notifications')} />
          <QuickNavBtn icon={<Users size={18} />} label="社区" onClick={() => nav('/community')} />
          <QuickNavBtn icon={<SettingsIcon size={18} />} label="设置" onClick={() => nav('/settings')} />
        </div>
      </div>
      {trans && (
        <div className="fixed inset-0" style={{ zIndex: 50, pointerEvents: 'none' }}>
          <div style={{ position: 'absolute', left: trans.cx, top: trans.cy, width: 0, height: 0, borderRadius: '50%', backgroundColor: trans.color, transform: 'translate(-50%,-50%)', animation: 'orb-expand ' + TRANSITION_MS + 'ms cubic-bezier(0.4,0,0.2,1) forwards', opacity: 0.85 }} />
        </div>
      )}
      <style>{`@keyframes orb-expand { 0% { width:0;height:0;opacity:0.9 } 100% { width:300vmax;height:300vmax;opacity:0.4 } }`}</style>
    </div>
  );
}

function QuickNavBtn({ icon, label, onClick }: { icon: React.ReactNode; label: string; onClick: () => void }) {
  return (
    <button onClick={onClick} className="flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-colors hover:bg-black/5" style={{ minWidth: 48 }}>
      <span style={{ color: '#555' }}>{icon}</span>
      <span style={{ fontSize: 10, color: '#888', fontWeight: 500 }}>{label}</span>
    </button>
  );
}

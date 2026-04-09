import { useEffect, useRef } from 'react';
import type { RefObject } from 'react';
import {
  BG, DPR, FISH_MAX, FISH_MIN, FISH_POWER, FISH_PUSH, FISH_R_FACTOR,
  INITIAL_PAN_Y, FRICTION, VEL_THRESHOLD, VEL_CAP,
  TAP_THRESHOLD_DESKTOP, TAP_THRESHOLD_MOBILE, TAP_HIT_PADDING_MOBILE,
  drawBubble, type DomainItem,
} from '@/lib/utils/home-canvas-utils';

/**
 * Manages the infinite-scroll fisheye hex-grid canvas for the HomePage.
 * Handles pointer interaction (pan/inertia/tap), rendering loop, and bubble hit-testing.
 */
export function useHomeCanvas(
  canvasRef: RefObject<HTMLCanvasElement | null>,
  sorted: DomainItem[],
  hexGrid: Array<{ x: number; y: number }>,
  totalSlots: number,
  wrapW: number, wrapH: number,
  baseR: number,
  onBubbleTap: (domain: DomainItem, screenX: number, screenY: number) => void,
) {
  const N = sorted.length;
  const tapRef = useRef(onBubbleTap);
  tapRef.current = onBubbleTap;

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
        const tapX = e.clientX - rect.left, tapY = e.clientY - rect.top;
        const W = cvs.width / DPR, H = cvs.height / DPR;
        const centerX = W / 2, centerY = H / 2;
        const fishR = Math.min(W, H) * FISH_R_FACTOR;
        const hits: { idx: number; sx: number; sy: number; sr: number }[] = [];
        for (let i = 0; i < totalSlots; i++) {
          const bx = hexGrid[i].x + s.panX, by = hexGrid[i].y + s.panY;
          let bestDx = bx, bestDy = by;
          for (const ox of [-wrapW, 0, wrapW]) for (const oy of [-wrapH, 0, wrapH]) {
            const cx = bx + ox, cy = by + oy;
            if (cx * cx + cy * cy < bestDx * bestDx + bestDy * bestDy) { bestDx = cx; bestDy = cy; }
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
            tapRef.current(sorted[h.idx % N], rect.left + h.sx, rect.top + h.sy);
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
        for (const ox of [-wrapW, 0, wrapW]) for (const oy of [-wrapH, 0, wrapH]) {
          const cx = baseX + ox, cy = baseY + oy;
          if (cx * cx + cy * cy < bestDx * bestDx + bestDy * bestDy) { bestDx = cx; bestDy = cy; }
        }
        const screenDist = Math.sqrt(bestDx * bestDx + bestDy * bestDy);
        const t = Math.max(0, 1 - screenDist / fishR);
        if (t <= 0) continue;
        const curve = Math.pow(t, FISH_POWER);
        const scale = FISH_MIN + (FISH_MAX - FISH_MIN) * curve;
        const push = 1 + curve * FISH_PUSH;
        const sx = centerX + bestDx * push, sy = centerY + bestDy * push;
        const sr = _baseR * scale, alpha = Math.pow(t, 3.0);
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
  }, [sorted, N, hexGrid, totalSlots, wrapW, wrapH, baseR, canvasRef]);
}

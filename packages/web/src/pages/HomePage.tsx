import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { Loader, BarChart3, Trophy, Settings as SettingsIcon, StickyNote, Users, History, Map, FileText, Bell } from 'lucide-react';
import { WelcomeGuide } from '@/components/common/WelcomeGuide';
import { ReviewBanner } from '@/components/common/ReviewBanner';
import { DailyRecommendation } from '@/components/common/DailyRecommendation';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import { useHomeCanvas } from '@/lib/hooks/useHomeCanvas';
import {
  DEMO_DOMAINS, NAME_MAP, BG, TRANSITION_MS,
  BASE_R, HEX_SPACING,
  completeness, buildRectHexGrid,
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

  useEffect(() => { fetchDomains().then(() => { if (useDomainStore.getState().domains.length === 0) useDomainStore.setState({ domains: DEMO_DOMAINS, loading: false, error: null }); }); }, [fetchDomains]);
  useEffect(() => { alive.current = true; return () => { alive.current = false; if (timerRef.current) clearTimeout(timerRef.current); }; }, []);

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

  const handleBubbleTap = useCallback((d: DomainItem, screenX: number, screenY: number) => {
    setTrans({ id: d.id, cx: screenX, cy: screenY, color: d.color });
    timerRef.current = setTimeout(() => { if (alive.current) navRef.current('/domain/' + d.id); }, TRANSITION_MS);
  }, []);

  useHomeCanvas(canvasRef, sorted, gridData.positions, gridData.totalSlots, gridData.wrapW, gridData.wrapH, baseR, handleBubbleTap);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: BG }}>
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" style={{ touchAction: 'none' }} />
      <div className="absolute left-0 right-0 text-center pointer-events-none select-none" style={{ top: 32, zIndex: 10 }}>
        <h1 className="text-xl font-semibold text-[var(--color-text-primary)] tracking-wide mb-1.5" style={{ textShadow: '0 1px 12px rgba(240,240,236,0.95)' }}>选择你的知识领域</h1>
        <p className="text-xs text-[var(--color-text-tertiary)] tracking-widest" style={{ textShadow: '0 1px 8px rgba(240,240,236,0.9)' }}>拖动浏览 · 点击进入 3D 知识图谱</p>
      </div>
      {loading && active.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin text-[var(--color-text-tertiary)]" />
        </div>
      )}
      <ReviewBanner />
      <DailyRecommendation />
      <WelcomeGuide />
      <div className="absolute bottom-6 left-1/2 -translate-x-1/2 pointer-events-auto" style={{ zIndex: 15 }}>
        <div className="flex items-center gap-2 px-3 py-2 rounded-2xl glass-heavy">
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
    <button onClick={onClick} className="flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-colors hover:bg-black/5 min-w-12">
      <span className="text-[var(--color-text-secondary)]">{icon}</span>
      <span className="text-[10px] text-[var(--color-text-tertiary)] font-medium">{label}</span>
    </button>
  );
}

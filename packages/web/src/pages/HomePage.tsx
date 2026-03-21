import { useEffect, useMemo, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader, Sparkles, BookOpen, GitBranch } from 'lucide-react';

/* ─── Demo fallback ─── */
const DEMO_DOMAINS: import('@akg/shared').Domain[] = [
  { id: 'ai-engineering', name: 'AI编程', icon: '', description: '', color: '#8b5cf6', is_active: true, stats: { total_concepts: 400, total_edges: 615, subdomains: 15 } },
  { id: 'mathematics', name: '数学', icon: '', description: '', color: '#3b82f6', is_active: true, stats: { total_concepts: 269, total_edges: 366, subdomains: 12 } },
  { id: 'game-engine', name: '游戏引擎', icon: '', description: '', color: '#059669', is_active: true, stats: { total_concepts: 300, total_edges: 319, subdomains: 15 } },
  { id: 'game-design', name: '游戏设计', icon: '', description: '', color: '#dc2626', is_active: true, stats: { total_concepts: 250, total_edges: 274, subdomains: 12 } },
  { id: 'psychology', name: '心理学', icon: '', description: '', color: '#a855f7', is_active: true, stats: { total_concepts: 183, total_edges: 203, subdomains: 8 } },
  { id: 'physics', name: '物理', icon: '', description: '', color: '#22c55e', is_active: true, stats: { total_concepts: 194, total_edges: 232, subdomains: 10 } },
  { id: 'english', name: '英语', icon: '', description: '', color: '#eab308', is_active: true, stats: { total_concepts: 200, total_edges: 229, subdomains: 10 } },
];

const NAME_MAP: Record<string, string> = { 'ai-engineering': 'AI编程' };

/* ─── Icon map for domains ─── */
const ICON_MAP: Record<string, string> = {
  'ai-engineering': '🤖', mathematics: '📐', 'game-engine': '🎮',
  'game-design': '🎲', psychology: '🧠', physics: '⚛️', english: '📖',
  'qa-testing': '🧪', 'project-management': '📋', 'financial': '💰',
  'narrative-design': '✍️',
};

/* ─── Helpers ─── */
function completeness(c: number, e: number, s: number) { return c + e * 0.5 + s * 5; }

const TRANSITION_MS = 800;

/* ─── Honeycomb positions ─── */
// Generate positions in expanding hex-ring order, centered at origin
function hexPositions(count: number): { col: number; row: number }[] {
  const positions: { col: number; row: number }[] = [{ col: 0, row: 0 }];
  if (count <= 1) return positions.slice(0, count);

  // Ring directions for hex grid (offset coordinates)
  const dirs = [
    [1, 0], [0, 1], [-1, 1], [-1, 0], [0, -1], [1, -1],
  ];

  let ring = 1;
  while (positions.length < count) {
    let col = ring, row = 0;
    for (let d = 0; d < 6 && positions.length < count; d++) {
      for (let s = 0; s < ring && positions.length < count; s++) {
        positions.push({ col, row });
        col += dirs[d][0];
        row += dirs[d][1];
      }
    }
    ring++;
  }
  return positions.slice(0, count);
}

/* ═════════════════════════════════════════════════════
   HomePage — Honeycomb Grid with Dark Tech Aesthetic
   Inspired by Apple Watch icon layout
   ═════════════════════════════════════════════════════ */
export function HomePage() {
  const nav = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const active = domains.filter(d => d.is_active !== false);
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [trans, setTrans] = useState<{ id: string; color: string } | null>(null);
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

  /* ─── Sorted domain list ─── */
  interface DomainItem {
    id: string; name: string; color: string; icon: string;
    concepts: number; edges: number; subs: number; comp: number;
  }
  const sorted = useMemo<DomainItem[]>(() => {
    if (!active.length) return [];
    const items = active.map(d => {
      const c = d.stats?.total_concepts ?? 0, e = d.stats?.total_edges ?? 0, s = d.stats?.subdomains ?? 0;
      return {
        id: d.id, name: NAME_MAP[d.id] || d.name, color: d.color,
        icon: ICON_MAP[d.id] || '📚',
        concepts: c, edges: e, subs: s, comp: completeness(c, e, s),
      };
    });
    items.sort((a, b) => b.comp - a.comp);
    return items;
  }, [active]);

  const hexPos = useMemo(() => hexPositions(sorted.length), [sorted.length]);

  const handleClick = useCallback((d: DomainItem) => {
    setTrans({ id: d.id, color: d.color });
    timerRef.current = setTimeout(() => {
      if (alive.current) navRef.current('/domain/' + d.id);
    }, TRANSITION_MS);
  }, []);

  const hoveredDomain = sorted.find(d => d.id === hoveredId);

  /* ─── Responsive cell sizing ─── */
  const CELL_SIZE = typeof window !== 'undefined' && window.innerWidth < 640 ? 96 : 128;
  const GAP = typeof window !== 'undefined' && window.innerWidth < 640 ? 8 : 12;

  return (
    <div className="homepage-root">
      {/* Ambient background effects */}
      <div className="homepage-bg-glow" />
      <div className="homepage-bg-grid" />

      {/* Header */}
      <motion.header
        className="homepage-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="homepage-logo">
          <Sparkles size={18} strokeWidth={1.5} />
          <span>AKG</span>
        </div>
        <h1 className="homepage-title">知识图谱</h1>
        <p className="homepage-subtitle">
          选择一个领域，探索知识的连接
        </p>
      </motion.header>

      {/* Honeycomb Grid */}
      <div className="homepage-grid-wrap">
        <div className="homepage-grid" style={{ '--cell': `${CELL_SIZE}px`, '--gap': `${GAP}px` } as React.CSSProperties}>
          {sorted.map((d, i) => {
            const pos = hexPos[i];
            const isOddRow = ((pos.row % 2) + 2) % 2 === 1;
            const xOffset = pos.col * (CELL_SIZE + GAP) + (isOddRow ? (CELL_SIZE + GAP) / 2 : 0);
            const yOffset = pos.row * ((CELL_SIZE + GAP) * 0.866);
            const isHovered = hoveredId === d.id;
            const isTransitioning = trans?.id === d.id;

            return (
              <motion.button
                key={d.id}
                className="homepage-cell"
                style={{
                  '--accent': d.color,
                  transform: `translate(${xOffset}px, ${yOffset}px)`,
                  width: CELL_SIZE,
                  height: CELL_SIZE,
                } as React.CSSProperties}
                initial={{ opacity: 0, scale: 0.5 }}
                animate={{
                  opacity: isTransitioning ? 0 : 1,
                  scale: isTransitioning ? 1.5 : 1,
                }}
                transition={{
                  delay: i * 0.06,
                  duration: 0.5,
                  ease: [0.22, 1, 0.36, 1],
                }}
                whileHover={{ scale: 1.12, zIndex: 10 }}
                whileTap={{ scale: 0.95 }}
                onHoverStart={() => setHoveredId(d.id)}
                onHoverEnd={() => setHoveredId(null)}
                onClick={() => handleClick(d)}
              >
                {/* Glow ring */}
                <div className="cell-glow" style={{ opacity: isHovered ? 1 : 0 }} />
                {/* Inner content */}
                <div className="cell-inner">
                  <span className="cell-icon">{d.icon}</span>
                  <span className="cell-name">{d.name}</span>
                </div>
                {/* Subtle border */}
                <div className="cell-border" />
              </motion.button>
            );
          })}
        </div>
      </div>

      {/* Bottom info panel — shows hovered domain stats */}
      <AnimatePresence mode="wait">
        {hoveredDomain ? (
          <motion.div
            key={hoveredDomain.id}
            className="homepage-info"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.2 }}
          >
            <div className="info-name" style={{ color: hoveredDomain.color }}>
              <span className="info-icon">{hoveredDomain.icon}</span>
              {hoveredDomain.name}
            </div>
            <div className="info-stats">
              <span><BookOpen size={13} strokeWidth={1.5} /> {hoveredDomain.concepts} 知识点</span>
              <span className="info-dot" />
              <span><GitBranch size={13} strokeWidth={1.5} /> {hoveredDomain.subs} 子领域</span>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="hint"
            className="homepage-hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            点击领域进入 3D 知识图谱
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading */}
      {loading && active.length === 0 && (
        <div className="homepage-loading">
          <Loader size={24} className="animate-spin" />
        </div>
      )}

      {/* Transition overlay */}
      <AnimatePresence>
        {trans && (
          <motion.div
            className="homepage-transition"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: TRANSITION_MS / 1000, ease: 'easeInOut' }}
            style={{ backgroundColor: trans.color }}
          />
        )}
      </AnimatePresence>

      <style>{`
        .homepage-root {
          position: relative;
          width: 100%;
          height: 100dvh;
          overflow: hidden;
          background: #0a0a0f;
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        /* ── Ambient background ── */
        .homepage-bg-glow {
          position: absolute;
          inset: 0;
          background:
            radial-gradient(ellipse 80% 60% at 50% 40%, rgba(99,102,241,0.08) 0%, transparent 70%),
            radial-gradient(ellipse 60% 50% at 30% 60%, rgba(16,185,129,0.05) 0%, transparent 60%),
            radial-gradient(ellipse 50% 40% at 75% 30%, rgba(139,92,246,0.06) 0%, transparent 50%);
          pointer-events: none;
        }
        .homepage-bg-grid {
          position: absolute;
          inset: 0;
          background-image:
            linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
          background-size: 48px 48px;
          mask-image: radial-gradient(ellipse 70% 60% at 50% 45%, black 30%, transparent 70%);
          pointer-events: none;
        }

        /* ── Header ── */
        .homepage-header {
          position: relative;
          z-index: 10;
          text-align: center;
          padding: 48px 24px 24px;
          flex-shrink: 0;
        }
        .homepage-logo {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 4px 14px 4px 10px;
          border-radius: 100px;
          background: rgba(255,255,255,0.06);
          border: 1px solid rgba(255,255,255,0.08);
          color: rgba(255,255,255,0.5);
          font-size: 12px;
          font-weight: 500;
          letter-spacing: 0.08em;
          margin-bottom: 20px;
          backdrop-filter: blur(8px);
        }
        .homepage-title {
          font-family: "Inter", "Noto Sans SC", -apple-system, system-ui, sans-serif;
          font-size: clamp(28px, 4vw, 40px);
          font-weight: 200;
          letter-spacing: -0.03em;
          color: rgba(255,255,255,0.92);
          margin: 0 0 8px;
          line-height: 1.2;
        }
        .homepage-subtitle {
          font-size: 14px;
          color: rgba(255,255,255,0.35);
          font-weight: 400;
          letter-spacing: 0.02em;
        }

        /* ── Grid wrapper ── */
        .homepage-grid-wrap {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          position: relative;
          z-index: 5;
          padding: 16px;
        }
        .homepage-grid {
          position: relative;
          /* Center the grid: offset by half the bounding box */
        }

        /* ── Cell ── */
        .homepage-cell {
          position: absolute;
          border-radius: 50%;
          cursor: pointer;
          border: none;
          background: none;
          padding: 0;
          outline: none;
          /* Center-anchor the grid */
          margin-left: calc(var(--cell) / -2);
          margin-top: calc(var(--cell) / -2);
          -webkit-tap-highlight-color: transparent;
        }
        .cell-inner {
          position: relative;
          z-index: 2;
          width: 100%;
          height: 100%;
          border-radius: 50%;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 4px;
          background: radial-gradient(circle at 35% 30%,
            rgba(255,255,255,0.08) 0%,
            rgba(255,255,255,0.02) 50%,
            rgba(0,0,0,0.1) 100%
          );
          backdrop-filter: blur(12px);
          transition: background 0.3s ease;
        }
        .homepage-cell:hover .cell-inner {
          background: radial-gradient(circle at 35% 30%,
            color-mix(in srgb, var(--accent) 20%, transparent) 0%,
            color-mix(in srgb, var(--accent) 8%, transparent) 50%,
            rgba(0,0,0,0.05) 100%
          );
        }
        .cell-border {
          position: absolute;
          inset: 0;
          border-radius: 50%;
          border: 1px solid rgba(255,255,255,0.08);
          pointer-events: none;
          transition: border-color 0.3s ease;
        }
        .homepage-cell:hover .cell-border {
          border-color: color-mix(in srgb, var(--accent) 40%, transparent);
        }
        .cell-glow {
          position: absolute;
          inset: -20%;
          border-radius: 50%;
          background: radial-gradient(circle, var(--accent) 0%, transparent 70%);
          opacity: 0;
          filter: blur(24px);
          transition: opacity 0.4s ease;
          pointer-events: none;
          z-index: 0;
        }
        .cell-icon {
          font-size: clamp(24px, 3vw, 36px);
          line-height: 1;
          filter: saturate(0.9);
        }
        .cell-name {
          font-family: "Inter", "Noto Sans SC", -apple-system, system-ui, sans-serif;
          font-size: clamp(11px, 1.2vw, 13px);
          font-weight: 500;
          color: rgba(255,255,255,0.7);
          letter-spacing: 0.01em;
          white-space: nowrap;
          transition: color 0.3s ease;
        }
        .homepage-cell:hover .cell-name {
          color: rgba(255,255,255,0.95);
        }

        /* ── Bottom info ── */
        .homepage-info {
          position: absolute;
          bottom: 48px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 10;
          text-align: center;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
        }
        .info-name {
          display: flex;
          align-items: center;
          gap: 8px;
          font-family: "Inter", "Noto Sans SC", system-ui, sans-serif;
          font-size: 18px;
          font-weight: 500;
          letter-spacing: -0.01em;
        }
        .info-icon { font-size: 20px; }
        .info-stats {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 13px;
          color: rgba(255,255,255,0.4);
        }
        .info-stats span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
        .info-dot {
          width: 3px; height: 3px;
          border-radius: 50%;
          background: rgba(255,255,255,0.2);
        }
        .homepage-hint {
          position: absolute;
          bottom: 52px;
          left: 50%;
          transform: translateX(-50%);
          z-index: 10;
          font-size: 13px;
          color: rgba(255,255,255,0.25);
          letter-spacing: 0.02em;
          white-space: nowrap;
        }

        /* ── Loading ── */
        .homepage-loading {
          position: absolute;
          inset: 0;
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 20;
          color: rgba(255,255,255,0.4);
        }

        /* ── Transition overlay ── */
        .homepage-transition {
          position: fixed;
          inset: 0;
          z-index: 50;
          opacity: 0;
        }

        /* ── Mobile adjustments ── */
        @media (max-width: 640px) {
          .homepage-header { padding: 32px 20px 16px; }
          .homepage-title { font-weight: 300; }
          .homepage-info { bottom: 36px; }
        }
      `}</style>
    </div>
  );
}

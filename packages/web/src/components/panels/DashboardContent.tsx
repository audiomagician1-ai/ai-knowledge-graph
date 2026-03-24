/**
 * DashboardContent — Two-column learning progress panel.
 *
 * Left column: current domain (header + stats + recent activity + mastered concepts)
 * Right column: other domains sorted by most-recently-accessed
 */
import { useEffect, useMemo } from 'react';
import { useLearningStore, peekDomainProgress, type ConceptProgress } from '@/lib/store/learning';
import { useGraphStore } from '@/lib/store/graph';
import { useDomainStore } from '@/lib/store/domain';
import { Zap, BookOpen, Flame, Trophy, Clock, Target, ArrowRight, Globe } from 'lucide-react';
import type { Domain } from '@akg/shared';

interface DashboardContentProps {
  /** Called when user clicks a learning activity item. Receives the concept_id. */
  onNavigate?: (conceptId: string) => void;
  /** Called when user switches to a different domain from the right panel. */
  onDomainSwitch?: (domainId: string) => void;
}

export function DashboardContent({ onNavigate, onDomainSwitch }: DashboardContentProps) {
  const { stats, progress, streak, computeStats, refreshStreak } = useLearningStore();
  const { graphData } = useGraphStore();
  const activeDomainId = useDomainStore((s) => s.activeDomain);
  const allDomains = useDomainStore((s) => s.domains);
  const domainInfo = useMemo(() => allDomains.find(d => d.id === activeDomainId), [allDomains, activeDomainId]);
  const otherDomains = useMemo(
    () => allDomains
      .filter(d => d.id !== activeDomainId && d.is_active !== false)
      .sort((a, b) => {
        const h = useDomainStore.getState().accessHistory;
        return (h[b.id] || 0) - (h[a.id] || 0);
      }),
    [allDomains, activeDomainId],
  );
  const { switchDomain } = useDomainStore();
  const { loadGraphData } = useGraphStore();

  useEffect(() => {
    refreshStreak();
    if (graphData) computeStats(graphData.nodes.length);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Zustand stable refs
  }, [graphData]);

  // Build concept ID → label lookup from graph data
  const nameMap = useMemo(() => {
    const m: Record<string, string> = {};
    if (graphData) for (const n of graphData.nodes) m[n.id] = n.label;
    return m;
  }, [graphData]);

  // Build recent activity from progress entries (sorted by last_learn_at)
  const recentActivity = Object.values(progress)
    .filter(p => p.last_learn_at > 0)
    .sort((a, b) => b.last_learn_at - a.last_learn_at)
    .slice(0, 6);
  const masteredNodes = Object.values(progress).filter(p => p.status === 'mastered');
  const learningNodes = Object.values(progress).filter(p => p.status === 'learning');
  const totalNodes = stats?.total_concepts || 0;
  const progressPct = totalNodes > 0 ? Math.round((masteredNodes.length / totalNodes) * 100) : 0;

  const handleDomainClick = (domainId: string) => {
    switchDomain(domainId);
    loadGraphData(domainId);
    onDomainSwitch?.(domainId);
  };

  return (
    <div style={{ display: 'flex', height: '100%', minHeight: 0 }}>
      {/* ─── Left column: Current domain ─── */}
      <div style={{ flex: '1 1 0', minWidth: 0, padding: '20px 24px', overflowY: 'auto' }}>
        {/* Domain header */}
        {domainInfo && (
          <div className="flex items-center gap-2.5" style={{ marginBottom: 18 }}>
            <span
              className="flex items-center justify-center rounded-lg text-lg"
              style={{ width: 36, height: 36, backgroundColor: `${domainInfo.color}15` }}
              role="img" aria-label={domainInfo.name}
            >
              {domainInfo.icon}
            </span>
            <div>
              <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--color-text-primary)' }}>{domainInfo.name}</div>
              <div style={{ fontSize: 11, color: 'var(--color-text-tertiary)', marginTop: 1 }}>当前学习</div>
            </div>
          </div>
        )}

        {/* Stats 2x2 grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 10, marginBottom: 16 }}>
          {[
            { label: '已掌握', value: masteredNodes.length, color: 'var(--color-accent-emerald)', icon: Zap },
            { label: '学习中', value: learningNodes.length, color: 'var(--color-accent-amber)', icon: BookOpen },
            { label: '连续', value: `${streak.current}天`, color: 'var(--color-accent-cyan)', icon: Flame },
            { label: '最高', value: `${streak.longest}天`, color: 'var(--color-text-tertiary)', icon: Trophy },
          ].map(({ label, value, color, icon: Icon }) => (
            <div key={label} style={{ borderRadius: 10, padding: '12px 8px', textAlign: 'center', backgroundColor: 'var(--color-surface-2)' }}>
              <Icon size={14} style={{ color, margin: '0 auto 6px' }} />
              <div className="font-bold font-mono" style={{ fontSize: 18, color }}>{value}</div>
              <div style={{ fontSize: 10, marginTop: 6, color: 'var(--color-text-tertiary)' }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Progress bar */}
        <div style={{ borderRadius: 10, padding: '14px 16px', backgroundColor: 'var(--color-surface-2)', marginBottom: 16 }}>
          <div className="flex items-center justify-between" style={{ marginBottom: 8 }}>
            <span style={{ fontSize: 12, fontWeight: 600 }}>掌握进度</span>
            <span className="font-mono font-bold" style={{ fontSize: 14, color: 'var(--color-accent-primary)' }}>{progressPct}%</span>
          </div>
          <div style={{ height: 8, borderRadius: 999, overflow: 'hidden', backgroundColor: 'var(--color-surface-4)' }}>
            <div style={{ height: '100%', borderRadius: 999, transition: 'all 0.7s', width: `${progressPct}%`, backgroundColor: 'var(--color-accent-emerald)', minWidth: progressPct > 0 ? 4 : 0 }} />
          </div>
          <div style={{ fontSize: 11, marginTop: 8, color: 'var(--color-text-tertiary)' }}>
            {masteredNodes.length} / {totalNodes} 概念
          </div>
        </div>

        {/* Recent activity */}
        <div style={{ marginBottom: 16 }}>
          <div className="flex items-center gap-2" style={{ marginBottom: 10 }}>
            <Clock size={13} style={{ color: 'var(--color-text-tertiary)' }} />
            <span style={{ fontSize: 13, fontWeight: 600 }}>最近学习</span>
          </div>
          {recentActivity.length === 0 ? (
            <p style={{ fontSize: 13, textAlign: 'center', padding: '28px 0', color: 'var(--color-text-tertiary)' }}>还没有学习记录</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
              {recentActivity.map((item) => (
                <ActivityRow key={item.concept_id} item={item} nameMap={nameMap} onNavigate={onNavigate} />
              ))}
            </div>
          )}
        </div>

        {/* Mastered concepts */}
        {masteredNodes.length > 0 && (
          <div>
            <div className="flex items-center gap-2" style={{ marginBottom: 10 }}>
              <Target size={12} style={{ color: 'var(--color-accent-emerald)' }} />
              <span style={{ fontSize: 13, fontWeight: 600 }}>已掌握</span>
              <span className="font-mono" style={{ fontSize: 10, padding: '1px 7px', borderRadius: 6, backgroundColor: 'rgba(138,173,122,0.1)', color: 'var(--color-accent-emerald)' }}>
                {masteredNodes.length}
              </span>
            </div>
            <div className="flex flex-wrap" style={{ gap: 6 }}>
              {masteredNodes.map((p) => (
                <button
                  key={p.concept_id}
                  onClick={() => onNavigate?.(p.concept_id)}
                  style={{ borderRadius: 7, padding: '5px 12px', fontSize: 11, backgroundColor: 'rgba(138,173,122,0.06)', color: 'var(--color-accent-emerald)', border: 'none', cursor: onNavigate ? 'pointer' : 'default' }}
                >
                  {nameMap[p.concept_id] || p.concept_id.replace(/-/g, ' ')}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* ─── Divider ─── */}
      <div style={{ width: 1, backgroundColor: 'var(--color-border)', flexShrink: 0 }} />

      {/* ─── Right column: Other domains ─── */}
      <div style={{ width: 240, flexShrink: 0, padding: '20px 16px', overflowY: 'auto' }}>
        <div className="flex items-center gap-2" style={{ marginBottom: 14 }}>
          <Globe size={13} style={{ color: 'var(--color-text-tertiary)' }} />
          <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>其他星系</span>
        </div>

        {otherDomains.length === 0 ? (
          <p style={{ fontSize: 12, textAlign: 'center', padding: '24px 0', color: 'var(--color-text-tertiary)' }}>暂无其他星系</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {otherDomains.map((domain) => (
              <OtherDomainCard key={domain.id} domain={domain} onClick={() => handleDomainClick(domain.id)} />
            ))}
          </div>
        )}

        {/* Coming soon hint */}
        <div
          className="flex items-center gap-2 mt-3 rounded-lg"
          style={{
            padding: '10px 12px',
            backgroundColor: 'var(--color-surface-2)',
            border: '1px dashed var(--color-border)',
          }}
        >
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            更多星系即将推出…
          </span>
        </div>
      </div>
    </div>
  );
}

/** Compact domain card for the right panel */
function OtherDomainCard({ domain, onClick }: { domain: Domain; onClick: () => void }) {
  const conceptCount = domain.stats?.total_concepts ?? domain.concept_count ?? 0;
  const progress = peekDomainProgress(domain.id);
  const pct = conceptCount > 0 ? Math.round((progress.mastered / conceptCount) * 100) : 0;
  const accessHistory = useDomainStore((s) => s.accessHistory);
  const lastAccess = accessHistory[domain.id];
  const timeAgo = lastAccess ? formatTimeAgo(lastAccess) : null;

  return (
    <button
      onClick={onClick}
      className="w-full text-left rounded-lg transition-all"
      style={{
        padding: '10px 12px',
        backgroundColor: 'var(--color-surface-2)',
        border: '1px solid var(--color-border)',
        cursor: 'pointer',
      }}
      onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-surface-3)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
    >
      <div className="flex items-center gap-2.5">
        <span
          className="flex items-center justify-center shrink-0 rounded-md text-base"
          style={{ width: 30, height: 30, backgroundColor: `${domain.color}15` }}
        >
          {domain.icon}
        </span>
        <div className="flex-1 min-w-0">
          <div className="truncate" style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {domain.name}
          </div>
          <div className="flex items-center gap-2 mt-0.5">
            <span style={{ fontSize: 10, color: 'var(--color-text-tertiary)' }}>{conceptCount} 概念</span>
            {progress.mastered > 0 && (
              <span style={{ fontSize: 10, color: 'var(--color-accent-emerald)' }}>{progress.mastered} ✓</span>
            )}
          </div>
        </div>
      </div>

      {/* Mini progress bar */}
      {conceptCount > 0 && (
        <div className="mt-2 flex items-center gap-2">
          <div
            className="flex-1 rounded-full overflow-hidden"
            style={{ height: 3, backgroundColor: 'var(--color-surface-4)' }}
          >
            <div
              style={{
                height: '100%',
                borderRadius: 999,
                width: `${pct}%`,
                backgroundColor: domain.color,
                minWidth: pct > 0 ? 2 : 0,
                transition: 'width 0.4s ease',
              }}
            />
          </div>
          <span style={{ fontSize: 10, color: 'var(--color-text-tertiary)', minWidth: 22, textAlign: 'right' }} className="font-mono">
            {pct}%
          </span>
        </div>
      )}

      {/* Last accessed */}
      {timeAgo && (
        <div style={{ fontSize: 10, color: 'var(--color-text-tertiary)', marginTop: 4 }}>
          {timeAgo}
        </div>
      )}
    </button>
  );
}

/** Format epoch ms as relative time (e.g., "3分钟前", "2天前") */
function formatTimeAgo(epochMs: number): string {
  const diff = Date.now() - epochMs;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}小时前`;
  const days = Math.floor(hours / 24);
  if (days < 30) return `${days}天前`;
  return `${Math.floor(days / 30)}个月前`;
}

function ActivityRow({ item, nameMap, onNavigate }: { item: ConceptProgress; nameMap: Record<string, string>; onNavigate?: (conceptId: string) => void }) {
  const time = new Date(item.last_learn_at);
  const timeStr = `${time.getMonth() + 1}/${time.getDate()} ${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}`;
  const isMastered = item.status === 'mastered';
  const hasScore = (item.mastery_score || 0) > 0;
  const scoreColor = hasScore
    ? (item.mastery_score >= 80 ? 'var(--color-accent-emerald)' : item.mastery_score >= 60 ? 'var(--color-accent-primary)' : 'var(--color-accent-rose)')
    : 'var(--color-text-tertiary)';
  const displayName = nameMap[item.concept_id] || item.concept_id.replace(/-/g, ' ');
  const clickable = !!onNavigate;
  return (
    <button
      onClick={() => onNavigate?.(item.concept_id)}
      disabled={!clickable}
      className="w-full flex items-center transition-all group"
      style={{ gap: 10, borderRadius: 8, padding: '8px 12px', backgroundColor: 'transparent', border: 'none', cursor: clickable ? 'pointer' : 'default', textAlign: 'left' }}
      onMouseEnter={(e) => { if (clickable) e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.04)'; }}
      onMouseLeave={(e) => { if (clickable) e.currentTarget.style.backgroundColor = 'transparent'; }}
    >
      <div className="flex items-center justify-center shrink-0" style={{ width: 28, height: 28, borderRadius: 7, backgroundColor: isMastered ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', color: isMastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}>
        {isMastered ? <Zap size={12} /> : <BookOpen size={12} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate" style={{ fontSize: 13 }}>{displayName}</div>
        <div className="font-mono" style={{ fontSize: 11, marginTop: 2, color: 'var(--color-text-tertiary)' }}>{timeStr}</div>
      </div>
      {hasScore ? (
        <span className="font-bold font-mono" style={{ fontSize: 14, color: scoreColor }}>{item.mastery_score}</span>
      ) : (
        <span style={{ fontSize: 11, color: 'var(--color-accent-amber)' }}>学习中</span>
      )}
      {clickable && <ArrowRight size={13} className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />}
    </button>
  );
}

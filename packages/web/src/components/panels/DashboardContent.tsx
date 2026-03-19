import { useEffect, useMemo } from 'react';
import { useLearningStore, type ConceptProgress } from '@/lib/store/learning';
import { useGraphStore } from '@/lib/store/graph';
import { useDomainStore } from '@/lib/store/domain';
import { Zap, BookOpen, Flame, Trophy, Clock, Target, ArrowRight } from 'lucide-react';
import { DomainOverview } from './DomainOverview';

interface DashboardContentProps {
  /** Called when user clicks a learning activity item. Receives the concept_id. */
  onNavigate?: (conceptId: string) => void;
}

export function DashboardContent({ onNavigate }: DashboardContentProps) {
  const { stats, progress, streak, computeStats, refreshStreak } = useLearningStore();
  const { graphData } = useGraphStore();
  const domainInfo = useDomainStore((s) => s.getActiveDomainInfo());

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
  // This ensures nodes show up as soon as user starts learning, even before assessment
  const recentActivity = Object.values(progress)
    .filter(p => p.last_learn_at > 0)
    .sort((a, b) => b.last_learn_at - a.last_learn_at)
    .slice(0, 6);
  const masteredNodes = Object.values(progress).filter(p => p.status === 'mastered');
  const learningNodes = Object.values(progress).filter(p => p.status === 'learning');
  const totalNodes = stats?.total_concepts || 0;
  const progressPct = totalNodes > 0 ? Math.round((masteredNodes.length / totalNodes) * 100) : 0;

  return (
    <div style={{ padding: '24px 28px', display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Galaxy Overview — all domains */}
      <DomainOverview compact />

      {/* Active domain header */}
      {domainInfo && (
        <div className="flex items-center gap-2" style={{ marginTop: -8 }}>
          <span role="img" aria-label={domainInfo.name}>{domainInfo.icon}</span>
          <span style={{ fontSize: 14, fontWeight: 600, color: domainInfo.color }}>{domainInfo.name}</span>
          <span style={{ fontSize: 12, color: 'var(--color-text-tertiary)' }}>学习进度</span>
        </div>
      )}

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 12 }}>
        {[
          { label: '已掌握', value: masteredNodes.length, color: 'var(--color-accent-emerald)', icon: Zap },
          { label: '学习中', value: learningNodes.length, color: 'var(--color-accent-amber)', icon: BookOpen },
          { label: '连续', value: `${streak.current}天`, color: 'var(--color-accent-cyan)', icon: Flame },
          { label: '最高', value: `${streak.longest}天`, color: 'var(--color-text-tertiary)', icon: Trophy },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} style={{ borderRadius: 10, padding: '16px 10px', textAlign: 'center', backgroundColor: 'var(--color-surface-2)' }}>
            <Icon size={16} style={{ color, margin: '0 auto 8px' }} />
            <div className="font-bold font-mono" style={{ fontSize: 20, color }}>{value}</div>
            <div style={{ fontSize: 11, marginTop: 8, color: 'var(--color-text-tertiary)' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Progress */}
      <div style={{ borderRadius: 10, padding: '18px 20px', backgroundColor: 'var(--color-surface-2)' }}>
        <div className="flex items-center justify-between" style={{ marginBottom: 12 }}>
          <span style={{ fontSize: 13, fontWeight: 600 }}>掌握进度</span>
          <span className="font-mono font-bold" style={{ fontSize: 16, color: 'var(--color-accent-primary)' }}>{progressPct}%</span>
        </div>
        <div style={{ height: 10, borderRadius: 999, overflow: 'hidden', backgroundColor: 'var(--color-surface-4)' }}>
          <div style={{ height: '100%', borderRadius: 999, transition: 'all 0.7s', width: `${progressPct}%`, backgroundColor: 'var(--color-accent-emerald)', minWidth: progressPct > 0 ? 4 : 0 }} />
        </div>
        <div style={{ fontSize: 13, marginTop: 10, color: 'var(--color-text-tertiary)' }}>
          {masteredNodes.length} / {totalNodes} 概念
        </div>
      </div>

      {/* Recent */}
      <div>
        <div className="flex items-center gap-2" style={{ marginBottom: 12 }}>
          <Clock size={15} style={{ color: 'var(--color-text-tertiary)' }} />
          <span style={{ fontSize: 14, fontWeight: 600 }}>最近学习</span>
        </div>
        {recentActivity.length === 0 ? (
          <p style={{ fontSize: 14, textAlign: 'center', padding: '36px 0', color: 'var(--color-text-tertiary)' }}>还没有学习记录</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {recentActivity.map((item) => (
              <ActivityRow key={item.concept_id} item={item} nameMap={nameMap} onNavigate={onNavigate} />
            ))}
          </div>
        )}
      </div>

      {/* Mastered */}
      {masteredNodes.length > 0 && (
        <div>
          <div className="flex items-center gap-2" style={{ marginBottom: 14 }}>
            <Target size={13} style={{ color: 'var(--color-accent-emerald)' }} />
            <span style={{ fontSize: 14, fontWeight: 500 }}>已掌握</span>
            <span className="font-mono" style={{ fontSize: 11, padding: '2px 8px', borderRadius: 6, backgroundColor: 'rgba(138,173,122,0.1)', color: 'var(--color-accent-emerald)' }}>
              {masteredNodes.length}
            </span>
          </div>
          <div className="flex flex-wrap" style={{ gap: 8 }}>
            {masteredNodes.map((p) => (
              <span key={p.concept_id} style={{ borderRadius: 8, padding: '6px 14px', fontSize: 12, backgroundColor: 'rgba(138,173,122,0.06)', color: 'var(--color-accent-emerald)' }}>
                {nameMap[p.concept_id] || p.concept_id.replace(/-/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ActivityRow({ item, nameMap, onNavigate }: { item: ConceptProgress; nameMap: Record<string, string>; onNavigate?: (conceptId: string) => void }) {
  const time = new Date(item.last_learn_at);
  const timeStr = `${time.getMonth() + 1}/${time.getDate()} ${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}`;
  const isMastered = item.status === 'mastered';
  const hasScore = (item.mastery_score || 0) > 0;
  const scoreColor = hasScore
    ? (item.mastery_score >= 80 ? 'var(--color-accent-emerald)' : item.mastery_score >= 60 ? 'var(--color-accent-primary)' : 'var(--color-accent-rose)')
    : 'var(--color-text-tertiary)';
  // Display concept name from graph data, fallback to humanized ID
  const displayName = nameMap[item.concept_id] || item.concept_id.replace(/-/g, ' ');
  const clickable = !!onNavigate;
  return (
    <button
      onClick={() => onNavigate?.(item.concept_id)}
      disabled={!clickable}
      className="w-full flex items-center transition-all group"
      style={{ gap: 12, borderRadius: 8, padding: '10px 16px', backgroundColor: 'transparent', border: 'none', cursor: clickable ? 'pointer' : 'default', textAlign: 'left' }}
      onMouseEnter={(e) => { if (clickable) e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.04)'; }}
      onMouseLeave={(e) => { if (clickable) e.currentTarget.style.backgroundColor = 'transparent'; }}
    >
      <div className="flex items-center justify-center shrink-0" style={{ width: 32, height: 32, borderRadius: 8, backgroundColor: isMastered ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', color: isMastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}>
        {isMastered ? <Zap size={13} /> : <BookOpen size={13} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate" style={{ fontSize: 14 }}>{displayName}</div>
        <div className="font-mono" style={{ fontSize: 12, marginTop: 4, color: 'var(--color-text-tertiary)' }}>{timeStr}</div>
      </div>
      {hasScore ? (
        <span className="font-bold font-mono" style={{ fontSize: 15, color: scoreColor }}>{item.mastery_score}</span>
      ) : (
        <span style={{ fontSize: 12, color: 'var(--color-accent-amber)' }}>学习中</span>
      )}
      {clickable && <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />}
    </button>
  );
}

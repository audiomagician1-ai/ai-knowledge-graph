import { useEffect } from 'react';
import { useLearningStore, type LearningHistory } from '@/lib/store/learning';
import { useGraphStore } from '@/lib/store/graph';
import { Zap, BookOpen, Flame, Trophy, Clock, Target } from 'lucide-react';

export function DashboardContent() {
  const { stats, progress, history, streak, computeStats, refreshStreak } = useLearningStore();
  const { graphData } = useGraphStore();

  useEffect(() => {
    refreshStreak();
    if (graphData) computeStats(graphData.nodes.length);
  }, [graphData]);

  const recentHistory = [...history].reverse().slice(0, 6);
  const masteredNodes = Object.values(progress).filter(p => p.status === 'mastered');
  const learningNodes = Object.values(progress).filter(p => p.status === 'learning');
  const totalNodes = stats?.total_concepts || 0;
  const progressPct = totalNodes > 0 ? Math.round((masteredNodes.length / totalNodes) * 100) : 0;

  return (
    <div style={{ padding: '28px 32px', display: 'flex', flexDirection: 'column', gap: 28 }}>
      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
        {[
          { label: '已掌握', value: masteredNodes.length, color: 'var(--color-accent-emerald)', icon: Zap },
          { label: '学习中', value: learningNodes.length, color: 'var(--color-accent-amber)', icon: BookOpen },
          { label: '连续', value: `${streak.current}天`, color: 'var(--color-accent-cyan)', icon: Flame },
          { label: '最高', value: `${streak.longest}天`, color: 'var(--color-text-tertiary)', icon: Trophy },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} style={{ borderRadius: 12, padding: '20px 12px', textAlign: 'center', backgroundColor: 'var(--color-surface-2)' }}>
            <Icon size={18} style={{ color, margin: '0 auto 12px' }} />
            <div className="font-bold font-mono" style={{ fontSize: 22, color }}>{value}</div>
            <div style={{ fontSize: 12, marginTop: 10, color: 'var(--color-text-tertiary)' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Progress */}
      <div style={{ borderRadius: 12, padding: 24, backgroundColor: 'var(--color-surface-2)' }}>
        <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
          <span style={{ fontSize: 14, fontWeight: 600 }}>掌握进度</span>
          <span className="font-mono font-bold" style={{ fontSize: 18, color: 'var(--color-accent-primary)' }}>{progressPct}%</span>
        </div>
        <div style={{ height: 10, borderRadius: 999, overflow: 'hidden', backgroundColor: 'var(--color-surface-4)' }}>
          <div style={{ height: '100%', borderRadius: 999, transition: 'all 0.7s', width: `${progressPct}%`, backgroundColor: 'var(--color-accent-emerald)', minWidth: progressPct > 0 ? 4 : 0 }} />
        </div>
        <div style={{ fontSize: 14, marginTop: 14, color: 'var(--color-text-tertiary)' }}>
          {masteredNodes.length} / {totalNodes} 概念
        </div>
      </div>

      {/* Recent */}
      <div>
        <div className="flex items-center gap-2.5" style={{ marginBottom: 16 }}>
          <Clock size={15} style={{ color: 'var(--color-text-tertiary)' }} />
          <span style={{ fontSize: 14, fontWeight: 600 }}>最近学习</span>
        </div>
        {recentHistory.length === 0 ? (
          <p style={{ fontSize: 14, textAlign: 'center', padding: '36px 0', color: 'var(--color-text-tertiary)' }}>还没有学习记录</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {recentHistory.map((item, i) => (
              <HistoryRow key={`${item.concept_id}-${i}`} item={item} />
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
                {p.concept_id.replace(/_/g, ' ')}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function HistoryRow({ item }: { item: LearningHistory }) {
  const time = new Date(item.timestamp);
  const timeStr = `${time.getMonth() + 1}/${time.getDate()} ${String(time.getHours()).padStart(2, '0')}:${String(time.getMinutes()).padStart(2, '0')}`;
  const scoreColor = item.score >= 80 ? 'var(--color-accent-emerald)' : item.score >= 60 ? 'var(--color-accent-primary)' : 'var(--color-accent-rose)';
  return (
    <div className="flex items-center" style={{ gap: 14, borderRadius: 10, padding: '14px 20px', backgroundColor: 'transparent' }}>
      <div className="flex items-center justify-center shrink-0" style={{ width: 32, height: 32, borderRadius: 8, backgroundColor: item.mastered ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', color: item.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}>
        {item.mastered ? <Zap size={13} /> : <BookOpen size={13} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="truncate" style={{ fontSize: 14 }}>{item.concept_name}</div>
        <div className="font-mono" style={{ fontSize: 12, marginTop: 4, color: 'var(--color-text-tertiary)' }}>{timeStr}</div>
      </div>
      <span className="font-bold font-mono" style={{ fontSize: 15, color: scoreColor }}>{item.score}</span>
    </div>
  );
}

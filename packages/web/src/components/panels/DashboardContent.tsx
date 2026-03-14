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
    <div className="p-5 space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-4 gap-2.5">
        {[
          { label: '已掌握', value: masteredNodes.length, color: 'var(--color-accent-emerald)', icon: Zap },
          { label: '学习中', value: learningNodes.length, color: 'var(--color-accent-primary)', icon: BookOpen },
          { label: '连续', value: `${streak.current}天`, color: 'var(--color-accent-warm)', icon: Flame },
          { label: '最高', value: `${streak.longest}天`, color: 'var(--color-text-tertiary)', icon: Trophy },
        ].map(({ label, value, color, icon: Icon }) => (
          <div key={label} className="rounded-xl p-3.5" style={{ backgroundColor: 'var(--color-surface-2)' }}>
            <Icon size={14} style={{ color, marginBottom: 6 }} />
            <div className="text-lg font-bold font-mono" style={{ color }}>{value}</div>
            <div className="text-[11px] mt-0.5" style={{ color: 'var(--color-text-tertiary)' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Progress */}
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-2)' }}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">掌握进度</span>
          <span className="text-sm font-mono font-semibold" style={{ color: 'var(--color-accent-primary)' }}>{progressPct}%</span>
        </div>
        <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
          <div className="h-full rounded-full transition-all duration-700" style={{ width: `${progressPct}%`, backgroundColor: 'var(--color-accent-emerald)', minWidth: progressPct > 0 ? 4 : 0 }} />
        </div>
        <div className="text-xs mt-2" style={{ color: 'var(--color-text-tertiary)' }}>
          {masteredNodes.length} / {totalNodes} 概念
        </div>
      </div>

      {/* Recent */}
      <div>
        <div className="flex items-center gap-1.5 mb-3">
          <Clock size={13} style={{ color: 'var(--color-text-tertiary)' }} />
          <span className="text-sm font-medium">最近学习</span>
        </div>
        {recentHistory.length === 0 ? (
          <p className="text-sm text-center py-6" style={{ color: 'var(--color-text-tertiary)' }}>还没有学习记录</p>
        ) : (
          <div className="space-y-0.5">
            {recentHistory.map((item, i) => (
              <HistoryRow key={`${item.concept_id}-${i}`} item={item} />
            ))}
          </div>
        )}
      </div>

      {/* Mastered */}
      {masteredNodes.length > 0 && (
        <div>
          <div className="flex items-center gap-1.5 mb-3">
            <Target size={13} style={{ color: 'var(--color-accent-emerald)' }} />
            <span className="text-sm font-medium">已掌握</span>
            <span className="text-[11px] font-mono px-1.5 rounded-md" style={{ backgroundColor: 'rgba(138,173,122,0.1)', color: 'var(--color-accent-emerald)' }}>
              {masteredNodes.length}
            </span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {masteredNodes.map((p) => (
              <span key={p.concept_id} className="rounded-lg px-2.5 py-1 text-xs" style={{ backgroundColor: 'rgba(138,173,122,0.06)', color: 'var(--color-accent-emerald)' }}>
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
    <div className="flex items-center gap-3 rounded-lg px-3 py-2.5" style={{ backgroundColor: 'transparent' }}>
      <div className="w-5 h-5 rounded-md flex items-center justify-center shrink-0" style={{ backgroundColor: item.mastered ? 'rgba(138,173,122,0.1)' : 'rgba(200,149,108,0.1)', color: item.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-primary)' }}>
        {item.mastered ? <Zap size={11} /> : <BookOpen size={11} />}
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-sm truncate">{item.concept_name}</div>
        <div className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>{timeStr}</div>
      </div>
      <span className="text-sm font-bold font-mono" style={{ color: scoreColor }}>{item.score}</span>
    </div>
  );
}

import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLearningStore, type LearningHistory } from '@/lib/store/learning';
import { useGraphStore } from '@/lib/store/graph';
import {
  Zap, BookOpen, Flame, Trophy, ArrowRight, Clock, Target,
} from 'lucide-react';
import { useIsDesktop } from '@/lib/hooks/useMediaQuery';

export function DashboardPage() {
  const { stats, progress, history, streak, computeStats, refreshStreak } = useLearningStore();
  const { graphData } = useGraphStore();
  const navigate = useNavigate();
  const isDesktop = useIsDesktop();

  useEffect(() => {
    refreshStreak();
    if (graphData) computeStats(graphData.nodes.length);
  }, [graphData]);

  const recentHistory = [...history].reverse().slice(0, 8);
  const masteredNodes = Object.values(progress).filter(p => p.status === 'mastered');
  const learningNodes = Object.values(progress).filter(p => p.status === 'learning');
  const totalNodes = stats?.total_concepts || 0;
  const progressPct = totalNodes > 0 ? Math.round((masteredNodes.length / totalNodes) * 100) : 0;

  return (
    <div className="h-full overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="max-w-3xl mx-auto px-6 py-8">

        {/* Header */}
        <div className="mb-6 animate-fade-in">
          <h1 className="text-xl font-semibold mb-1">学习进度</h1>
          <p className="text-[13px]" style={{ color: 'var(--color-text-tertiary)' }}>
            {masteredNodes.length}/{totalNodes} 概念已掌握
          </p>
        </div>

        {/* Stats row */}
        <div className={`grid gap-3 mb-5 ${isDesktop ? 'grid-cols-4' : 'grid-cols-2'}`}>
          {[
            { label: '已掌握', value: masteredNodes.length, color: 'var(--color-accent-emerald)', icon: Zap },
            { label: '学习中', value: learningNodes.length, color: 'var(--color-accent-amber)', icon: BookOpen },
            { label: '连续', value: `${streak.current}天`, color: 'var(--color-accent-primary)', icon: Flame },
            { label: '最高', value: `${streak.longest}天`, color: 'var(--color-text-tertiary)', icon: Trophy },
          ].map(({ label, value, color, icon: Icon }, idx) => (
            <div
              key={label}
              className={`card-static p-4 animate-fade-in stagger-${idx + 1}`}
            >
              <Icon size={14} style={{ color, marginBottom: 8 }} />
              <div className="text-xl font-bold font-mono" style={{ color }}>{value}</div>
              <div className="text-[11px] mt-0.5" style={{ color: 'var(--color-text-tertiary)' }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Progress bar */}
        <div className="card-static p-4 mb-5 animate-fade-in stagger-3">
          <div className="flex items-center justify-between mb-2.5">
            <span className="text-[13px] font-medium">掌握进度</span>
            <span className="text-[13px] font-mono font-semibold" style={{ color: 'var(--color-accent-primary)' }}>{progressPct}%</span>
          </div>
          <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${progressPct}%`,
                backgroundColor: 'var(--color-accent-emerald)',
                minWidth: progressPct > 0 ? 6 : 0,
              }}
            />
          </div>
        </div>

        {/* Two columns */}
        <div className={`grid gap-4 ${isDesktop ? 'grid-cols-5' : 'grid-cols-1'}`}>
          {/* Recent activity */}
          <div className={`${isDesktop ? 'col-span-3' : ''} card-static p-4 animate-fade-in stagger-4`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-1.5">
                <Clock size={13} style={{ color: 'var(--color-text-tertiary)' }} />
                <span className="text-[13px] font-medium">最近学习</span>
              </div>
            </div>
            {recentHistory.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-[13px] mb-3" style={{ color: 'var(--color-text-tertiary)' }}>还没有学习记录</p>
                <button onClick={() => navigate('/graph')} className="btn-primary text-[13px] px-5 py-2">
                  前往图谱 <ArrowRight size={13} className="inline ml-1" />
                </button>
              </div>
            ) : (
              <div className="space-y-0.5">
                {recentHistory.map((item, i) => (
                  <HistoryItem key={`${item.concept_id}-${item.timestamp}-${i}`} item={item} navigate={navigate} />
                ))}
              </div>
            )}
          </div>

          {/* Mastered */}
          <div className={`${isDesktop ? 'col-span-2' : ''} card-static p-4 animate-fade-in stagger-5`}>
            <div className="flex items-center gap-1.5 mb-3">
              <Target size={13} style={{ color: 'var(--color-accent-emerald)' }} />
              <span className="text-[13px] font-medium">已掌握</span>
              {masteredNodes.length > 0 && (
                <span className="text-[10px] font-mono px-1.5 py-px rounded" style={{ backgroundColor: 'rgba(52,211,153,0.1)', color: 'var(--color-accent-emerald)' }}>
                  {masteredNodes.length}
                </span>
              )}
            </div>
            {masteredNodes.length === 0 ? (
              <p className="text-[12px] py-6 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
                通过评估后概念会出现在这里
              </p>
            ) : (
              <div className="flex flex-wrap gap-1">
                {masteredNodes.map((p) => (
                  <button
                    key={p.concept_id}
                    onClick={() => navigate('/graph')}
                    className="rounded px-2 py-0.5 text-[11px] font-medium transition-colors"
                    style={{ backgroundColor: 'rgba(52,211,153,0.06)', color: 'var(--color-accent-emerald)', border: '1px solid rgba(52,211,153,0.1)' }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(52,211,153,0.12)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'rgba(52,211,153,0.06)')}
                  >
                    {p.concept_id.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function HistoryItem({ item, navigate }: { item: LearningHistory; navigate: (p: string) => void }) {
  const time = new Date(item.timestamp);
  const timeStr = `${time.getMonth() + 1}/${time.getDate()} ${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`;
  const scoreColor = item.score >= 80 ? 'var(--color-accent-emerald)' : item.score >= 60 ? 'var(--color-accent-amber)' : 'var(--color-accent-rose)';

  return (
    <button
      onClick={() => navigate('/graph')}
      className="w-full flex items-center gap-2.5 rounded-lg px-2.5 py-2 transition-all group"
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
    >
      <div
        className="w-6 h-6 rounded flex items-center justify-center shrink-0"
        style={{
          backgroundColor: item.mastered ? 'rgba(52,211,153,0.1)' : 'rgba(234,179,8,0.1)',
          color: item.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)',
        }}
      >
        {item.mastered ? <Zap size={11} /> : <BookOpen size={11} />}
      </div>
      <div className="flex-1 min-w-0 text-left">
        <div className="text-[13px] font-medium truncate">{item.concept_name}</div>
        <div className="text-[10px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>{timeStr}</div>
      </div>
      <span className="text-[13px] font-bold font-mono" style={{ color: scoreColor }}>{item.score}</span>
      <ArrowRight size={12} className="opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: 'var(--color-text-tertiary)' }} />
    </button>
  );
}

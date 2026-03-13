import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLearningStore, type LearningHistory } from '@/lib/store/learning';
import { useGraphStore } from '@/lib/store/graph';
import {
  Zap, BookOpen, Circle, Layers, Flame, Trophy,
  ArrowRight, Clock, Target, TrendingUp, Compass,
} from 'lucide-react';

export function DashboardPage() {
  const { stats, progress, history, streak, computeStats, refreshStreak } = useLearningStore();
  const { graphData } = useGraphStore();
  const navigate = useNavigate();

  useEffect(() => {
    refreshStreak();
    if (graphData) {
      computeStats(graphData.nodes.length);
    }
  }, [graphData]);

  const recentHistory = [...history].reverse().slice(0, 10);
  const masteredNodes = Object.values(progress).filter(p => p.status === 'mastered');
  const learningNodes = Object.values(progress).filter(p => p.status === 'learning');

  const totalNodes = stats?.total_concepts || 0;
  const progressPct = totalNodes > 0 ? Math.round((masteredNodes.length / totalNodes) * 100) : 0;

  return (
    <div className="h-full overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="max-w-4xl mx-auto px-8 py-8">

        {/* Page header */}
        <div className="mb-8 animate-fade-in">
          <h1 className="text-2xl font-bold mb-1" style={{ color: 'var(--color-text-primary)' }}>
            学习进度
          </h1>
          <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
            Track your knowledge mastery journey
          </p>
        </div>

        {/* Top stats row */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          {[
            {
              label: '已掌握', value: masteredNodes.length, icon: Zap,
              color: 'var(--color-accent-emerald)',
              glow: 'var(--color-glow-emerald)',
              gradient: 'linear-gradient(135deg, rgba(52, 211, 153, 0.12), rgba(16, 185, 129, 0.06))',
            },
            {
              label: '学习中', value: learningNodes.length, icon: BookOpen,
              color: 'var(--color-accent-amber)',
              glow: 'var(--color-glow-amber)',
              gradient: 'linear-gradient(135deg, rgba(251, 191, 36, 0.12), rgba(245, 158, 11, 0.06))',
            },
            {
              label: '未开始', value: stats?.not_started_count ?? totalNodes, icon: Circle,
              color: 'var(--color-text-tertiary)',
              glow: 'none',
              gradient: 'linear-gradient(135deg, rgba(148, 163, 184, 0.06), transparent)',
            },
            {
              label: '总节点', value: totalNodes, icon: Layers,
              color: 'var(--color-accent-indigo)',
              glow: 'var(--color-glow-indigo)',
              gradient: 'linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.06))',
            },
          ].map(({ label, value, icon: Icon, color, gradient }, idx) => (
            <div
              key={label}
              className={`card-static rounded-2xl p-5 animate-fade-in stagger-${idx + 1}`}
              style={{ background: gradient }}
            >
              <div className="flex items-center justify-between mb-3">
                <div
                  className="w-9 h-9 rounded-xl flex items-center justify-center"
                  style={{ backgroundColor: color + '18', color }}
                >
                  <Icon size={18} />
                </div>
              </div>
              <div className="text-2xl font-bold font-mono" style={{ color }}>{value}</div>
              <div className="text-[12px] mt-0.5" style={{ color: 'var(--color-text-tertiary)' }}>{label}</div>
            </div>
          ))}
        </div>

        {/* Progress bar + Streak row */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {/* Progress */}
          <div className="col-span-2 card-static rounded-2xl p-5 animate-fade-in stagger-3">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <TrendingUp size={16} style={{ color: 'var(--color-accent-indigo)' }} />
                <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                  总体掌握进度
                </span>
              </div>
              <span className="text-xl font-bold font-mono" style={{ color: 'var(--color-accent-indigo)' }}>
                {progressPct}%
              </span>
            </div>
            <div className="h-3 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${progressPct}%`,
                  background: 'linear-gradient(90deg, var(--color-accent-indigo), var(--color-accent-violet))',
                  minWidth: progressPct > 0 ? 8 : 0,
                  boxShadow: '0 0 12px var(--color-glow-indigo)',
                }}
              />
            </div>
            <div className="flex justify-between mt-2 text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
              <span>{masteredNodes.length} mastered</span>
              <span>{totalNodes} total</span>
            </div>
          </div>

          {/* Streak */}
          <div className="card-static rounded-2xl p-5 animate-fade-in stagger-4">
            <div className="flex items-center gap-2 mb-3">
              <Flame size={16} style={{ color: 'var(--color-accent-amber)' }} />
              <span className="text-[12px] font-semibold" style={{ color: 'var(--color-text-secondary)' }}>
                学习连续
              </span>
            </div>
            <div className="mb-3">
              <span className="text-3xl font-bold font-mono" style={{ color: 'var(--color-accent-amber)' }}>
                {streak.current}
              </span>
              <span className="text-sm ml-1" style={{ color: 'var(--color-text-tertiary)' }}>天</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Trophy size={12} style={{ color: 'var(--color-accent-violet)' }} />
              <span className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                最高 {streak.longest} 天
              </span>
            </div>
          </div>
        </div>

        {/* Recent + Mastered row */}
        <div className="grid grid-cols-3 gap-4">
          {/* Recent history */}
          <div className="col-span-2 card-static rounded-2xl p-5 animate-fade-in stagger-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Clock size={16} style={{ color: 'var(--color-text-secondary)' }} />
                <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                  最近学习
                </span>
              </div>
              <span className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                Recent Activity
              </span>
            </div>

            {recentHistory.length === 0 ? (
              <div className="text-center py-10">
                <div
                  className="w-16 h-16 rounded-2xl mx-auto mb-4 flex items-center justify-center"
                  style={{
                    background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.08))',
                    border: '1px solid var(--color-border)',
                  }}
                >
                  <Compass size={28} style={{ color: 'var(--color-accent-indigo)' }} />
                </div>
                <p className="text-sm mb-1" style={{ color: 'var(--color-text-secondary)' }}>
                  还没有学习记录
                </p>
                <p className="text-[12px] mb-4" style={{ color: 'var(--color-text-tertiary)' }}>
                  去图谱选择一个概念开始你的学习旅程
                </p>
                <button onClick={() => navigate('/graph')} className="btn-primary text-[13px] px-6 py-2.5">
                  前往图谱
                  <ArrowRight size={14} className="inline ml-1" />
                </button>
              </div>
            ) : (
              <div className="space-y-1">
                {recentHistory.map((item, i) => (
                  <HistoryItem key={`${item.concept_id}-${item.timestamp}-${i}`} item={item} navigate={navigate} />
                ))}
              </div>
            )}
          </div>

          {/* Mastered concepts */}
          <div className="card-static rounded-2xl p-5 animate-fade-in stagger-6">
            <div className="flex items-center gap-2 mb-4">
              <Target size={16} style={{ color: 'var(--color-accent-emerald)' }} />
              <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                已掌握
              </span>
              {masteredNodes.length > 0 && (
                <span
                  className="text-[10px] font-mono px-1.5 py-0.5 rounded-md"
                  style={{ backgroundColor: 'var(--color-accent-emerald)' + '18', color: 'var(--color-accent-emerald)' }}
                >
                  {masteredNodes.length}
                </span>
              )}
            </div>

            {masteredNodes.length === 0 ? (
              <p className="text-[12px] py-6 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
                完成对话学习评估后，<br />掌握的概念会出现在这里
              </p>
            ) : (
              <div className="flex flex-wrap gap-1.5">
                {masteredNodes.map((p) => (
                  <button
                    key={p.concept_id}
                    onClick={() => navigate('/graph')}
                    className="rounded-lg px-2.5 py-1 text-[11px] font-medium transition-all"
                    style={{
                      backgroundColor: 'rgba(52, 211, 153, 0.08)',
                      color: 'var(--color-accent-emerald)',
                      border: '1px solid rgba(52, 211, 153, 0.15)',
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(52, 211, 153, 0.15)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'rgba(52, 211, 153, 0.08)')}
                  >
                    <Zap size={10} className="inline mr-1" />
                    {p.concept_id.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8 pb-4">
          <p className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
            AI Knowledge Graph v0.3.0 · Data stored locally in browser
          </p>
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
      className="w-full flex items-center gap-3 rounded-xl px-3 py-2.5 transition-all group"
      onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
      onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
    >
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
        style={{
          backgroundColor: item.mastered ? 'rgba(52, 211, 153, 0.12)' : 'rgba(251, 191, 36, 0.12)',
          color: item.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)',
        }}
      >
        {item.mastered ? <Zap size={14} /> : <BookOpen size={14} />}
      </div>
      <div className="flex-1 min-w-0 text-left">
        <div className="text-[13px] font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
          {item.concept_name}
        </div>
        <div className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>{timeStr}</div>
      </div>
      <div className="text-sm font-bold font-mono" style={{ color: scoreColor }}>
        {item.score}
      </div>
      <ArrowRight size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" style={{ color: 'var(--color-text-tertiary)' }} />
    </button>
  );
}

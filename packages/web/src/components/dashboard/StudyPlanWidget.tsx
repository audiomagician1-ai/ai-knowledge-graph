import { useState, useEffect } from 'react';
import { CalendarDays, BookOpen, RefreshCw, Sparkles, Clock } from 'lucide-react';

interface PlanItem {
  concept_id: string;
  name: string;
  domain_id: string;
  type: 'review' | 'continue' | 'new';
  estimated_minutes: number;
}

interface DayPlan {
  day: number;
  items: PlanItem[];
  total_minutes: number;
  review_count: number;
  learn_count: number;
}

interface PlanResponse {
  plan: DayPlan[];
  summary: {
    days: number;
    daily_minutes: number;
    total_items: number;
    total_review: number;
    total_learn: number;
    total_minutes: number;
  };
  queues: { review_pending: number; continue_pending: number; new_available: number };
}

const TYPE_STYLES: Record<string, { label: string; color: string; icon: typeof BookOpen }> = {
  review: { label: '复习', color: '#f59e0b', icon: RefreshCw },
  continue: { label: '继续', color: '#3b82f6', icon: BookOpen },
  new: { label: '新学', color: '#22c55e', icon: Sparkles },
};

export function StudyPlanWidget({ days = 3, dailyMinutes = 30 }: { days?: number; dailyMinutes?: number }) {
  const [data, setData] = useState<PlanResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeDay, setActiveDay] = useState(0);

  useEffect(() => {
    const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';
    fetch(`${base}/api/analytics/study-plan?days=${days}&daily_minutes=${dailyMinutes}`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [days, dailyMinutes]);

  if (loading) return (
    <section className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="h-5 w-36 rounded bg-white/10 mb-4" />
      <div className="space-y-2">{[1,2,3,4].map(i => <div key={i} className="h-10 rounded bg-white/5" />)}</div>
    </section>
  );

  if (!data || data.summary.total_items === 0) return null;

  const dayPlan = data.plan[activeDay];

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
        <CalendarDays size={18} style={{ color: '#8b5cf6' }} />
        学习计划
        <span className="text-xs font-normal opacity-50 ml-auto">
          {data.summary.total_items} 项 · {data.summary.total_minutes} 分钟
        </span>
      </h2>

      {/* Day tabs */}
      <div className="flex gap-2 mb-3 overflow-x-auto">
        {data.plan.map((d, i) => (
          <button
            key={i}
            onClick={() => setActiveDay(i)}
            className="px-3 py-1 rounded-full text-xs font-medium transition-all shrink-0"
            style={{
              backgroundColor: activeDay === i ? 'var(--color-accent)' : 'var(--color-surface-2)',
              color: activeDay === i ? 'var(--color-text-on-accent)' : 'inherit',
              opacity: activeDay === i ? 1 : 0.7,
            }}
          >
            第{d.day}天 · {d.items.length}项
          </button>
        ))}
      </div>

      {/* Day items */}
      {dayPlan && (
        <div className="space-y-2">
          {dayPlan.items.length === 0 && (
            <p className="text-sm opacity-50 text-center py-4">今日无学习任务</p>
          )}
          {dayPlan.items.slice(0, 8).map((item, i) => {
            const style = TYPE_STYLES[item.type] || TYPE_STYLES.new;
            const Icon = style.icon;
            return (
              <div key={i} className="flex items-center gap-3 rounded-lg px-3 py-2" style={{ backgroundColor: 'var(--color-surface-2)' }}>
                <Icon size={14} style={{ color: style.color }} />
                <span className="text-sm truncate flex-1">{item.name}</span>
                <span className="text-xs px-1.5 py-0.5 rounded-full" style={{ backgroundColor: `${style.color}20`, color: style.color }}>{style.label}</span>
                <span className="text-xs opacity-40 flex items-center gap-1"><Clock size={10} />{item.estimated_minutes}m</span>
              </div>
            );
          })}
          {dayPlan.items.length > 8 && (
            <p className="text-xs opacity-40 text-center">+{dayPlan.items.length - 8} 更多项目</p>
          )}
        </div>
      )}

      {/* Summary bar */}
      <div className="flex gap-4 mt-3 text-xs opacity-50">
        <span>📋 复习 {data.queues.review_pending}</span>
        <span>📚 继续 {data.queues.continue_pending}</span>
        <span>✨ 可学 {data.queues.new_available}</span>
      </div>
    </section>
  );
}
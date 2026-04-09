import { useEffect, useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Calendar, Trophy, BookOpen, Zap, Flame } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { useDashboardBatch } from '@/lib/hooks/useDashboardBatch';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface WeeklyData {
  period: { this_week: string; last_week: string };
  this_week: { mastered: number; started: number; assessments: number; active_days: number };
  last_week: { mastered: number; started: number; assessments: number; active_days: number };
  deltas: { mastered_pct: number; started_pct: number; assessments_pct: number; active_days_pct: number };
  overall: { total_mastered: number; total_learning: number; streak_current: number; streak_longest: number };
}

function DeltaBadge({ value }: { value: number }) {
  if (value > 0) {
    return (
      <span className="inline-flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded-full" style={{ backgroundColor: '#22c55e20', color: '#22c55e' }}>
        <TrendingUp size={12} /> +{value}%
      </span>
    );
  }
  if (value < 0) {
    return (
      <span className="inline-flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded-full" style={{ backgroundColor: '#ef444420', color: '#ef4444' }}>
        <TrendingDown size={12} /> {value}%
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded-full" style={{ backgroundColor: '#6b728020', color: '#6b7280' }}>
      <Minus size={12} /> 持平
    </span>
  );
}

function MetricRow({
  icon,
  label,
  current,
  previous,
  delta,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  current: number;
  previous: number;
  delta: number;
  color: string;
}) {
  return (
    <div className="flex items-center justify-between py-3 px-4 rounded-lg" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg" style={{ backgroundColor: `${color}20`, color }}>
          {icon}
        </div>
        <div>
          <p className="text-sm font-medium">{label}</p>
          <p className="text-xs opacity-50">上周: {previous}</p>
        </div>
      </div>
      <div className="text-right">
        <p className="text-lg font-bold" style={{ color }}>{current}</p>
        <DeltaBadge value={delta} />
      </div>
    </div>
  );
}

/**
 * WeeklyReport — Shows week-over-week learning progress comparison.
 */
export function WeeklyReport() {
  const batchData = useDashboardBatch('weekly_report');
  const [data, setData] = useState<WeeklyData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // V2.4: Use batch data if available
    if (batchData) {
      setData(batchData as unknown as WeeklyData);
      setLoading(false);
      return;
    }
    // Fallback: individual endpoint
    const load = async () => {
      try {
        const res = await fetchWithRetry(`${API_BASE}/analytics/weekly-report`);
        if (res.ok) {
          setData(await res.json());
        }
      } catch { /* silently fail — show nothing */ }
      finally { setLoading(false); }
    };
    load();
  }, [batchData]);

  if (loading) {
    return (
      <section className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <div className="h-6 w-32 rounded" style={{ backgroundColor: 'var(--color-surface-2)' }} />
        <div className="mt-4 space-y-3">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-16 rounded-lg" style={{ backgroundColor: 'var(--color-surface-0)' }} />
          ))}
        </div>
      </section>
    );
  }

  if (!data) return null;

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Calendar size={18} style={{ color: 'var(--color-accent)' }} />
          周报
        </h2>
        <span className="text-xs opacity-50">{data.period.this_week}</span>
      </div>

      <div className="space-y-2">
        <MetricRow
          icon={<Trophy size={16} />}
          label="概念掌握"
          current={data.this_week.mastered}
          previous={data.last_week.mastered}
          delta={data.deltas.mastered_pct}
          color="#22c55e"
        />
        <MetricRow
          icon={<BookOpen size={16} />}
          label="新概念开始"
          current={data.this_week.started}
          previous={data.last_week.started}
          delta={data.deltas.started_pct}
          color="#3b82f6"
        />
        <MetricRow
          icon={<Zap size={16} />}
          label="评估次数"
          current={data.this_week.assessments}
          previous={data.last_week.assessments}
          delta={data.deltas.assessments_pct}
          color="#f59e0b"
        />
        <MetricRow
          icon={<Flame size={16} />}
          label="活跃天数"
          current={data.this_week.active_days}
          previous={data.last_week.active_days}
          delta={data.deltas.active_days_pct}
          color="#ef4444"
        />
      </div>

      {/* Overall summary */}
      <div className="mt-4 pt-4 border-t grid grid-cols-2 gap-3" style={{ borderColor: 'var(--color-border)' }}>
        <div className="text-center">
          <p className="text-2xl font-bold" style={{ color: '#22c55e' }}>{data.overall.total_mastered}</p>
          <p className="text-xs opacity-50">总掌握</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold" style={{ color: '#ef4444' }}>
            {data.overall.streak_current}
            {data.overall.streak_longest > data.overall.streak_current && (
              <span className="text-sm opacity-40 ml-1">/ {data.overall.streak_longest} 最长</span>
            )}
          </p>
          <p className="text-xs opacity-50">连续天数</p>
        </div>
      </div>
    </section>
  );
}
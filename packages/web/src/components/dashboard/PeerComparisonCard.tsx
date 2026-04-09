import { useState, useEffect } from 'react';
import { Users, TrendingUp, Flame, Star, BookOpen } from 'lucide-react';

interface PeerData {
  user: {
    mastered: number;
    learning: number;
    avg_score: number;
    current_streak: number;
    active_days_90d: number;
    mastery_speed: number;
  };
  percentiles: Record<string, number>;
  comparison_labels: Record<string, string>;
  peer_count: number;
}

const METRIC_ICONS: Record<string, typeof Star> = {
  mastery_speed: TrendingUp,
  streak: Flame,
  avg_score: Star,
  total_mastered: BookOpen,
};

const METRIC_COLORS: Record<string, string> = {
  mastery_speed: '#3b82f6',
  streak: '#ef4444',
  avg_score: '#f59e0b',
  total_mastered: '#22c55e',
};

function PercentileBar({ label, percentile, color }: { label: string; percentile: number; color: string }) {
  const width = Math.max(2, percentile);
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs w-[90px] shrink-0 truncate" style={{ color: 'var(--color-text-secondary)' }}>
        {label}
      </span>
      <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
        <div
          className="h-full rounded-full transition-all duration-700"
          style={{ width: `${width}%`, backgroundColor: color }}
        />
      </div>
      <span className="text-xs font-semibold w-10 text-right" style={{ color }}>
        {percentile}%
      </span>
    </div>
  );
}

export function PeerComparisonCard() {
  const [data, setData] = useState<PeerData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';
    fetch(`${base}/api/analytics/peer-comparison`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <section className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="h-5 w-36 rounded bg-white/10 mb-4" />
      <div className="space-y-3">{[1,2,3,4].map(i => <div key={i} className="h-4 rounded bg-white/5" />)}</div>
    </section>
  );

  if (!data) return null;

  const avgPercentile = Math.round(
    Object.values(data.percentiles).reduce((a, b) => a + b, 0) / Math.max(1, Object.keys(data.percentiles).length)
  );

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center gap-2 mb-4">
        <Users size={16} style={{ color: '#8b5cf6' }} />
        <span className="font-medium text-sm">同伴对比</span>
        <span className="ml-auto text-xs px-2 py-0.5 rounded-full" style={{
          backgroundColor: avgPercentile >= 70 ? '#22c55e20' : avgPercentile >= 40 ? '#f59e0b20' : '#ef444420',
          color: avgPercentile >= 70 ? '#22c55e' : avgPercentile >= 40 ? '#f59e0b' : '#ef4444',
        }}>
          前 {100 - avgPercentile}%
        </span>
      </div>

      <div className="space-y-3">
        {Object.entries(data.percentiles).map(([key, pct]) => {
          const label = data.comparison_labels[key] || key;
          const color = METRIC_COLORS[key] || '#8b5cf6';
          return <PercentileBar key={key} label={label} percentile={pct} color={color} />;
        })}
      </div>

      <p className="text-xs mt-3 text-center" style={{ color: 'var(--color-text-secondary)' }}>
        基于 {data.peer_count} 位学习者的数据
      </p>
    </section>
  );
}
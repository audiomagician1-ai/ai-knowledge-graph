import { useEffect, useState } from 'react';
import { Clock, BarChart3 } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { useDashboardBatch } from '@/lib/hooks/useDashboardBatch';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface PatternData {
  period_days: number;
  hour_distribution: number[];
  weekday_distribution: Record<string, number>;
  peak_hour: number;
  peak_hour_label: string;
  peak_day: string;
  total_events: number;
  consistency_score: number;
}

/**
 * StudyPatterns — Visualize when the user studies (hour heatmap + weekday bars).
 */
export function StudyPatterns() {
  const batchData = useDashboardBatch('study_patterns');
  const [data, setData] = useState<PatternData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // V2.4: Use batch data if available
    if (batchData) {
      setData(batchData as unknown as PatternData);
      setLoading(false);
      return;
    }
    // Fallback: individual endpoint
    const load = async () => {
      try {
        const res = await fetchWithRetry(`${API_BASE}/analytics/study-patterns`);
        if (res.ok) {
          setData(await res.json());
        }
      } catch { /* silently fail */ }
      finally { setLoading(false); }
    };
    load();
  }, [batchData]);

  if (loading || !data || data.total_events === 0) return null;

  const maxHour = Math.max(1, ...data.hour_distribution);
  const weekdays = Object.entries(data.weekday_distribution);
  const maxWeekday = Math.max(1, ...weekdays.map(([, v]) => v));

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Clock size={18} style={{ color: '#8b5cf6' }} />
          学习习惯
        </h2>
        <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: '#8b5cf620', color: '#8b5cf6' }}>
          一致性 {data.consistency_score}%
        </span>
      </div>

      {/* Peak time badge */}
      <div className="flex gap-3 mb-4">
        <div className="flex-1 rounded-lg p-3" style={{ backgroundColor: 'var(--color-surface-0)' }}>
          <p className="text-xs opacity-50">高峰时段</p>
          <p className="font-bold text-sm" style={{ color: '#8b5cf6' }}>{data.peak_hour_label}</p>
        </div>
        <div className="flex-1 rounded-lg p-3" style={{ backgroundColor: 'var(--color-surface-0)' }}>
          <p className="text-xs opacity-50">最活跃</p>
          <p className="font-bold text-sm" style={{ color: '#f59e0b' }}>{data.peak_day}</p>
        </div>
      </div>

      {/* Hour distribution (24h mini bars) */}
      <div className="mb-4">
        <p className="text-xs opacity-50 mb-2 flex items-center gap-1">
          <BarChart3 size={12} /> 24小时分布
        </p>
        <div className="flex items-end gap-px h-12">
          {data.hour_distribution.map((count, hour) => {
            const height = (count / maxHour) * 100;
            const isActive = count > 0;
            const isPeak = hour === data.peak_hour;
            return (
              <div
                key={hour}
                className="flex-1 rounded-t transition-all"
                style={{
                  height: `${Math.max(2, height)}%`,
                  backgroundColor: isPeak ? '#8b5cf6' : isActive ? '#8b5cf640' : 'var(--color-surface-2)',
                }}
                title={`${hour}:00 — ${count} 次`}
              />
            );
          })}
        </div>
        <div className="flex justify-between mt-1">
          <span className="text-[10px] opacity-30">0时</span>
          <span className="text-[10px] opacity-30">6时</span>
          <span className="text-[10px] opacity-30">12时</span>
          <span className="text-[10px] opacity-30">18时</span>
          <span className="text-[10px] opacity-30">24时</span>
        </div>
      </div>

      {/* Weekday distribution */}
      <div>
        <p className="text-xs opacity-50 mb-2">每周分布</p>
        <div className="space-y-1.5">
          {weekdays.map(([day, count]) => {
            const width = (count / maxWeekday) * 100;
            const isPeak = day === data.peak_day;
            return (
              <div key={day} className="flex items-center gap-2">
                <span className="text-xs w-8 text-right opacity-60">{day}</span>
                <div className="flex-1 h-4 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
                  <div
                    className="h-full rounded-full transition-all"
                    style={{
                      width: `${Math.max(2, width)}%`,
                      backgroundColor: isPeak ? '#f59e0b' : '#f59e0b60',
                    }}
                  />
                </div>
                <span className="text-xs w-6 opacity-40">{count}</span>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
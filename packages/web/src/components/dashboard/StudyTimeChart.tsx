import { useState, useEffect } from 'react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { Clock, TrendingUp, Calendar } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface DailyEntry {
  date: string;
  minutes: number;
  concepts_touched: number;
}

interface StudyTimeSummary {
  total_minutes: number;
  total_hours: number;
  active_days: number;
  avg_daily_minutes: number;
  avg_weekly_minutes: number;
  total_concepts_touched: number;
  minutes_per_concept: number;
}

interface StudyTimeData {
  period_days: number;
  daily: DailyEntry[];
  summary: StudyTimeSummary;
}

/**
 * Study Time Chart — bar chart showing daily study time + summary metrics.
 * Dashboard widget (lazy-loadable).
 */
export function StudyTimeChart({ days = 14 }: { days?: number }) {
  const [data, setData] = useState<StudyTimeData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWithRetry(`${API_BASE}/analytics/study-time-report?days=${days}`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [days]);

  if (loading) return <div className="h-40 bg-white/5 rounded-lg animate-pulse" />;
  if (!data) return null;

  const { daily, summary } = data;
  const displayDays = daily.slice(-days);
  const maxMinutes = Math.max(1, ...displayDays.map((d) => d.minutes));

  // SVG bar chart dimensions
  const W = 320;
  const H = 100;
  const PAD = { t: 8, r: 8, b: 18, l: 4 };
  const plotW = W - PAD.l - PAD.r;
  const plotH = H - PAD.t - PAD.b;
  const barW = Math.max(2, plotW / displayDays.length - 2);

  return (
    <div className="bg-white/[0.03] border border-white/5 rounded-lg p-4 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Clock size={16} className="text-indigo-400" />
          <span className="text-sm font-medium">学习时间</span>
        </div>
        <span className="text-xs text-gray-500">最近 {days} 天</span>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center">
          <p className="text-lg font-bold text-indigo-400">{summary.total_hours}h</p>
          <p className="text-[10px] text-gray-500">总计</p>
        </div>
        <div className="text-center">
          <p className="text-lg font-bold text-blue-400">{summary.avg_daily_minutes}m</p>
          <p className="text-[10px] text-gray-500">日均</p>
        </div>
        <div className="text-center">
          <p className="text-lg font-bold text-green-400">{summary.active_days}</p>
          <p className="text-[10px] text-gray-500">活跃天</p>
        </div>
      </div>

      {/* Bar chart */}
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 100 }}>
        {displayDays.map((day, i) => {
          const x = PAD.l + (i * (plotW / displayDays.length)) + 1;
          const barH = (day.minutes / maxMinutes) * plotH;
          const y = PAD.t + plotH - barH;
          const isActive = day.minutes > 0;

          return (
            <g key={day.date}>
              <rect
                x={x}
                y={isActive ? y : PAD.t + plotH - 1}
                width={barW}
                height={isActive ? barH : 1}
                rx={1}
                fill={isActive ? 'rgb(99,102,241)' : 'rgba(255,255,255,0.05)'}
                opacity={isActive ? 0.8 : 0.3}
              />
            </g>
          );
        })}

        {/* X-axis: first and last date */}
        {displayDays.length > 0 && (
          <>
            <text x={PAD.l} y={H - 2} className="fill-gray-600 text-[7px]">{displayDays[0].date.slice(5)}</text>
            <text x={W - PAD.r} y={H - 2} textAnchor="end" className="fill-gray-600 text-[7px]">{displayDays[displayDays.length - 1].date.slice(5)}</text>
          </>
        )}
      </svg>

      {/* Productivity metric */}
      <div className="flex items-center justify-between text-[10px] text-gray-500">
        <div className="flex items-center gap-1">
          <TrendingUp size={10} />
          <span>{summary.minutes_per_concept}分/概念</span>
        </div>
        <div className="flex items-center gap-1">
          <Calendar size={10} />
          <span>{summary.total_concepts_touched} 概念学习</span>
        </div>
      </div>
    </div>
  );
}

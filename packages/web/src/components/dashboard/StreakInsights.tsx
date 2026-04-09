import { useState, useEffect } from 'react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { Flame, Target, Calendar, TrendingUp, Star } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface StreakData {
  current_streak: number;
  longest_streak: number;
  best_streak_90d: { start: string; length: number };
  total_active_days_90d: number;
  activity_rate_90d: number;
  habit_score: number;
  weekly_consistency: { consistent_weeks: number; total_weeks: number; rate: number };
  recent: { last_7_days: number; last_30_days: number };
  best_day: { name: string; activity_count: number };
  weekday_distribution: Record<string, number>;
}

/**
 * Streak Insights — habit formation analysis and consistency metrics.
 * Dashboard widget showing advanced streak analytics.
 */
export function StreakInsights() {
  const [data, setData] = useState<StreakData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWithRetry(`${API_BASE}/analytics/streak-insights`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="h-40 bg-white/5 rounded-lg animate-pulse" />;
  if (!data) return null;

  // Habit score color
  const scoreColor = data.habit_score >= 70 ? 'text-green-400' :
    data.habit_score >= 40 ? 'text-yellow-400' : 'text-red-400';
  const scoreBg = data.habit_score >= 70 ? 'bg-green-500/10' :
    data.habit_score >= 40 ? 'bg-yellow-500/10' : 'bg-red-500/10';

  // Weekday bars
  const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
  const maxDay = Math.max(1, ...weekdays.map((d) => data.weekday_distribution[d] || 0));

  return (
    <div className="bg-white/[0.03] border border-white/5 rounded-lg p-4 space-y-4">
      {/* Header with habit score */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Flame size={16} className="text-orange-400" />
          <span className="text-sm font-medium">学习习惯</span>
        </div>
        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full ${scoreBg}`}>
          <Star size={12} className={scoreColor} />
          <span className={`text-sm font-bold ${scoreColor}`}>{data.habit_score}</span>
          <span className="text-[10px] text-gray-500">/ 100</span>
        </div>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-4 gap-2">
        <div className="text-center p-2 rounded-lg bg-white/[0.03]">
          <p className="text-lg font-bold text-orange-400">{data.current_streak}</p>
          <p className="text-[10px] text-gray-500">当前连续</p>
        </div>
        <div className="text-center p-2 rounded-lg bg-white/[0.03]">
          <p className="text-lg font-bold text-yellow-400">{data.longest_streak}</p>
          <p className="text-[10px] text-gray-500">最长连续</p>
        </div>
        <div className="text-center p-2 rounded-lg bg-white/[0.03]">
          <p className="text-lg font-bold text-blue-400">{data.activity_rate_90d}%</p>
          <p className="text-[10px] text-gray-500">90天活跃</p>
        </div>
        <div className="text-center p-2 rounded-lg bg-white/[0.03]">
          <p className="text-lg font-bold text-green-400">{data.weekly_consistency.rate}%</p>
          <p className="text-[10px] text-gray-500">周一致性</p>
        </div>
      </div>

      {/* Weekday distribution mini bars */}
      <div>
        <div className="flex items-center gap-1 mb-2 text-[10px] text-gray-500">
          <Calendar size={10} />
          <span>每周学习分布</span>
          <span className="ml-auto">最佳: {data.best_day.name}</span>
        </div>
        <div className="flex items-end gap-1 h-8">
          {weekdays.map((day) => {
            const count = data.weekday_distribution[day] || 0;
            const h = (count / maxDay) * 100;
            const isBest = day === data.best_day.name;
            return (
              <div key={day} className="flex-1 flex flex-col items-center gap-0.5">
                <div
                  className="w-full rounded-t"
                  style={{
                    height: `${Math.max(2, h)}%`,
                    backgroundColor: isBest ? 'rgb(234,179,8)' : 'rgb(99,102,241)',
                    opacity: count > 0 ? 0.8 : 0.15,
                    minHeight: 2,
                  }}
                />
                <span className={`text-[8px] ${isBest ? 'text-yellow-400' : 'text-gray-600'}`}>{day.slice(1)}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent activity */}
      <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1 border-t border-white/5">
        <div className="flex items-center gap-1">
          <TrendingUp size={10} />
          <span>近7天: {data.recent.last_7_days}/7 天活跃</span>
        </div>
        <div className="flex items-center gap-1">
          <Target size={10} />
          <span>近30天: {data.recent.last_30_days}/30</span>
        </div>
      </div>
    </div>
  );
}

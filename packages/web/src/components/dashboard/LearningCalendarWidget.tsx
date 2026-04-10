/**
 * LearningCalendarWidget — Monthly learning activity calendar with FSRS due projections.
 * V4.4: GitHub-style intensity heatmap + future review schedule overlay.
 */
import { useState, useEffect } from 'react';
import { Calendar, BookOpen, Star, RotateCcw } from 'lucide-react';

interface DayCell {
  date: string; events_count: number; mastered_count: number;
  reviews_due: number; domains_active: number; intensity: number; is_future: boolean;
}
interface MonthData {
  month: string; label: string; days: DayCell[];
  total_events: number; total_mastered: number;
}
interface CalendarData {
  months: MonthData[];
  summary: {
    total_active_days: number; total_events: number;
    total_mastered: number; upcoming_reviews: number;
  };
}

const INTENSITY_COLORS = [
  'bg-white/5', 'bg-emerald-900/60', 'bg-emerald-700/60', 'bg-emerald-500/60', 'bg-emerald-400/80',
];
const FUTURE_BG = 'bg-blue-500/30';

export function LearningCalendarWidget({ months = 3 }: { months?: number }) {
  const [data, setData] = useState<CalendarData | null>(null);
  const [hoveredDay, setHoveredDay] = useState<DayCell | null>(null);

  useEffect(() => {
    fetch(`/api/analytics/learning-calendar?months=${months}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, [months]);

  if (!data) return null;

  const { summary: s } = data;
  // Show last 2 months by default
  const displayMonths = data.months.slice(-2);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Calendar size={16} className="text-emerald-400" />
        <h3 className="text-sm font-semibold">学习日历</h3>
        <span className="ml-auto text-xs opacity-40">
          {s.total_active_days} 天活跃
        </span>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-4 gap-2 mb-3 text-center">
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{s.total_active_days}</div>
          <div className="text-[10px] opacity-40">活跃天</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{s.total_events}</div>
          <div className="text-[10px] opacity-40">学习事件</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold text-emerald-400">{s.total_mastered}</div>
          <div className="text-[10px] opacity-40">掌握数</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold text-blue-400">{s.upcoming_reviews}</div>
          <div className="text-[10px] opacity-40">待复习</div>
        </div>
      </div>

      {/* Calendar grid */}
      {displayMonths.map(m => (
        <div key={m.month} className="mb-3 last:mb-0">
          <div className="text-[10px] opacity-40 mb-1 flex justify-between">
            <span>{m.label}</span>
            <span>{m.total_events} 事件 · {m.total_mastered} 掌握</span>
          </div>
          <div className="flex flex-wrap gap-[2px]">
            {m.days.map(d => {
              const hasDue = d.is_future && d.reviews_due > 0;
              const bg = hasDue ? FUTURE_BG : INTENSITY_COLORS[d.intensity] || INTENSITY_COLORS[0];
              return (
                <div
                  key={d.date}
                  className={`w-3 h-3 rounded-sm ${bg} cursor-pointer transition-all hover:ring-1 hover:ring-white/30`}
                  title={`${d.date}: ${d.events_count}事件, ${d.mastered_count}掌握, ${d.reviews_due}复习`}
                  onMouseEnter={() => setHoveredDay(d)}
                  onMouseLeave={() => setHoveredDay(null)}
                />
              );
            })}
          </div>
        </div>
      ))}

      {/* Hover tooltip */}
      {hoveredDay && (
        <div className="mt-2 p-2 bg-white/10 rounded-lg text-[10px] flex items-center gap-3">
          <span className="opacity-60">{hoveredDay.date}</span>
          {hoveredDay.events_count > 0 && (
            <span className="flex items-center gap-1"><BookOpen size={10} />{hoveredDay.events_count} 事件</span>
          )}
          {hoveredDay.mastered_count > 0 && (
            <span className="flex items-center gap-1 text-emerald-400"><Star size={10} />{hoveredDay.mastered_count} 掌握</span>
          )}
          {hoveredDay.reviews_due > 0 && (
            <span className="flex items-center gap-1 text-blue-400"><RotateCcw size={10} />{hoveredDay.reviews_due} 复习</span>
          )}
        </div>
      )}

      {/* Legend */}
      <div className="flex items-center gap-1 mt-2 text-[10px] opacity-30">
        <span>少</span>
        {INTENSITY_COLORS.map((c, i) => (
          <div key={i} className={`w-2.5 h-2.5 rounded-sm ${c}`} />
        ))}
        <span>多</span>
        <span className="ml-2">|</span>
        <div className={`w-2.5 h-2.5 rounded-sm ${FUTURE_BG} ml-1`} />
        <span>待复习</span>
      </div>
    </div>
  );
}

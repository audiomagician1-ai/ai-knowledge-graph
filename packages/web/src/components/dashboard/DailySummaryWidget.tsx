/**
 * DailySummaryWidget — "What should I do today?" compact summary card.
 * V4.5: Single API call aggregates streak, reviews, today's activity, and recommended action.
 */
import { useState, useEffect } from 'react';
import { Sun, Flame, RotateCcw, BookOpen, ArrowRight, Star } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SummaryData {
  date: string;
  streak: { current: number; longest: number };
  today: { events: number; mastered: number; domains_active: number };
  reviews: { due: number; overdue: number };
  progress: { total_mastered: number; total_learning: number; total_concepts: number };
  recommended_action: { type: string; label: string; priority: string; route: string };
  motivation: string;
}

const PRIORITY_COLORS: Record<string, string> = {
  high: 'bg-red-500/20 text-red-400 border-red-500/30',
  medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  low: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
};

export function DailySummaryWidget() {
  const [data, setData] = useState<SummaryData | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    fetch('/api/analytics/daily-summary')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const { streak, today, reviews, recommended_action: ra } = data;
  const prioClass = PRIORITY_COLORS[ra.priority] || PRIORITY_COLORS.low;

  return (
    <div className="rounded-xl border border-white/10 bg-gradient-to-br from-white/5 to-white/[0.02] p-4">
      <div className="flex items-center gap-2 mb-3">
        <Sun size={16} className="text-amber-400" />
        <h3 className="text-sm font-semibold">今日概览</h3>
        {streak.current > 0 && (
          <span className="ml-auto flex items-center gap-1 text-xs text-orange-400">
            <Flame size={12} />{streak.current}天
          </span>
        )}
      </div>

      {/* Motivation */}
      <div className="text-xs opacity-60 mb-3">{data.motivation}</div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="flex items-center justify-center gap-1">
            <BookOpen size={10} className="opacity-40" />
            <span className="text-sm font-bold">{today.events}</span>
          </div>
          <div className="text-[10px] opacity-40">今日学习</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="flex items-center justify-center gap-1">
            <Star size={10} className="text-emerald-400" />
            <span className="text-sm font-bold text-emerald-400">{today.mastered}</span>
          </div>
          <div className="text-[10px] opacity-40">今日掌握</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="flex items-center justify-center gap-1">
            <RotateCcw size={10} className="text-blue-400" />
            <span className="text-sm font-bold text-blue-400">{reviews.due}</span>
          </div>
          <div className="text-[10px] opacity-40">待复习</div>
        </div>
      </div>

      {/* Recommended action button */}
      <button
        onClick={() => nav(ra.route)}
        className={`w-full flex items-center gap-2 p-2.5 rounded-lg border transition-colors hover:brightness-110 ${prioClass}`}
      >
        <span className="text-xs font-medium flex-1 text-left">{ra.label}</span>
        <ArrowRight size={14} className="shrink-0 opacity-60" />
      </button>

      {/* Progress footnote */}
      <div className="flex justify-between mt-2 text-[10px] opacity-30">
        <span>已掌握 {data.progress.total_mastered} / {data.progress.total_concepts}</span>
        <span>进行中 {data.progress.total_learning}</span>
      </div>
    </div>
  );
}

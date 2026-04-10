/**
 * DifficultyTunerWidget — Auto-calibration suggestions for concept difficulty.
 * V4.3: Compares seed difficulty vs actual performance, flags deviations with
 * direction (too_easy/too_hard), confidence score, and suggested new difficulty.
 */
import { useState, useEffect } from 'react';
import { SlidersHorizontal, ArrowDown, ArrowUp, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Suggestion {
  concept_id: string; name: string; domain_id: string;
  seed_difficulty: number; observed_difficulty: number; suggested_difficulty: number;
  deviation: number; direction: string; confidence: number;
  avg_score: number; sessions: number;
}
interface TunerData {
  suggestions: Suggestion[];
  summary: { total_flagged: number; too_easy: number; too_hard: number };
}

export function DifficultyTunerWidget({ limit = 10 }: { limit?: number }) {
  const [data, setData] = useState<TunerData | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    fetch(`/api/analytics/difficulty-tuner?limit=${limit}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, [limit]);

  if (!data || data.suggestions.length === 0) return null;

  const { summary } = data;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <SlidersHorizontal size={16} className="text-amber-400" />
        <h3 className="text-sm font-semibold">难度校准建议</h3>
        <span className="ml-auto text-xs opacity-40">{summary.total_flagged} 待调整</span>
      </div>

      {/* Summary badges */}
      <div className="flex gap-2 mb-3">
        {summary.too_easy > 0 && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded-full text-[10px]">
            <ArrowDown size={10} /> {summary.too_easy} 偏简单
          </span>
        )}
        {summary.too_hard > 0 && (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-red-500/20 text-red-400 rounded-full text-[10px]">
            <ArrowUp size={10} /> {summary.too_hard} 偏困难
          </span>
        )}
      </div>

      {/* Suggestion list */}
      <div className="space-y-2">
        {data.suggestions.slice(0, 8).map(s => (
          <button
            key={s.concept_id}
            onClick={() => nav(`/graph?domain=${s.domain_id}&concept=${s.concept_id}`)}
            className="w-full flex items-start gap-2 p-2 bg-white/5 hover:bg-white/10 rounded-lg transition-colors text-left"
          >
            <div className="mt-0.5 shrink-0">
              {s.direction === 'too_easy'
                ? <ArrowDown size={14} className="text-emerald-400" />
                : <ArrowUp size={14} className="text-red-400" />}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium truncate">{s.name}</div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-[10px] opacity-40">难度 {s.seed_difficulty}→{s.suggested_difficulty}</span>
                <span className="text-[10px] opacity-30">|</span>
                <span className="text-[10px] opacity-40">均分 {s.avg_score}</span>
                <span className="text-[10px] opacity-30">|</span>
                <span className="text-[10px] opacity-40">置信度 {Math.round(s.confidence * 100)}%</span>
              </div>
            </div>
            {s.confidence >= 0.8 && (
              <AlertTriangle size={12} className="text-amber-400 opacity-60 shrink-0 mt-1" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}

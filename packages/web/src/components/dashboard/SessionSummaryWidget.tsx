/**
 * SessionSummaryWidget — Compact summary of recent learning session activity.
 * V3.1: Backend-powered via /api/analytics/session-summary.
 */
import { useState, useEffect } from 'react';
import { Activity, BookOpen, Trophy, Brain, Clock } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface DomainBreakdown { domain_id: string; domain_name: string; events: number }
interface ScoreInfo { score: number; concept_id: string; concept_name: string }

interface SummaryData {
  hours: number;
  total_events: number;
  concepts_touched: number;
  assessments: number;
  new_masteries: number;
  best_score: ScoreInfo | null;
  weakest: ScoreInfo | null;
  domain_breakdown: DomainBreakdown[];
  active_minutes: number;
  current_streak: number;
}

export function SessionSummaryWidget({ hours = 24 }: { hours?: number }) {
  const [data, setData] = useState<SummaryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchWithRetry(`${API_BASE}/analytics/session-summary?hours=${hours}`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [hours]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Activity size={16} style={{ color: 'var(--color-accent)' }} /> 学习小结
        </h3>
        <div className="animate-pulse h-16 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (!data || data.total_events === 0) return null;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Activity size={16} style={{ color: 'var(--color-accent)' }} />
        学习小结
        <span className="text-[10px] font-normal opacity-40 ml-auto">过去{hours}小时</span>
      </h3>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="flex items-center gap-1.5 text-xs">
          <BookOpen size={12} className="text-blue-400" />
          <span className="opacity-60">{data.concepts_touched} 概念</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <Brain size={12} className="text-purple-400" />
          <span className="opacity-60">{data.assessments} 评估</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <Trophy size={12} className="text-green-400" />
          <span className="opacity-60">{data.new_masteries} 新掌握</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <Clock size={12} className="text-amber-400" />
          <span className="opacity-60">{data.active_minutes}分钟</span>
        </div>
      </div>

      {/* Best score */}
      {data.best_score && (
        <p className="text-[10px] opacity-50 mb-1">
          最佳: {data.best_score.concept_name} ({data.best_score.score}分)
        </p>
      )}

      {/* Domain breakdown */}
      {data.domain_breakdown.length > 0 && (
        <div className="flex gap-1 flex-wrap mt-2">
          {data.domain_breakdown.slice(0, 4).map((d) => (
            <span key={d.domain_id} className="text-[10px] px-1.5 py-0.5 rounded-full opacity-60"
              style={{ backgroundColor: 'var(--color-surface-2)' }}>
              {d.domain_name} ×{d.events}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

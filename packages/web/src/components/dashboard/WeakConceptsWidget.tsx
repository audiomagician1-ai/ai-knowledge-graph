import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, TrendingDown, ArrowRight, Lightbulb } from 'lucide-react';

interface WeakConcept {
  concept_id: string;
  status: string;
  current_score: number;
  sessions: number;
  avg_score: number;
  score_trend: number[];
  weakness_score: number;
  reasons: string[];
  suggestion: string;
}

interface WeakResponse {
  weak_concepts: WeakConcept[];
  total_weak: number;
  total_assessed: number;
}

export function WeakConceptsWidget({ limit = 5 }: { limit?: number }) {
  const navigate = useNavigate();
  const [data, setData] = useState<WeakResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';
    fetch(`${base}/api/analytics/weak-concepts?limit=${limit}`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [limit]);

  if (loading) return (
    <section className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="h-5 w-32 rounded bg-white/10 mb-4" />
      <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-14 rounded-lg bg-white/5" />)}</div>
    </section>
  );

  if (!data || data.weak_concepts.length === 0) return null;

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
        <AlertTriangle size={18} style={{ color: '#ef4444' }} />
        薄弱概念
        <span className="text-xs font-normal opacity-50 ml-auto">{data.total_weak} 个需关注</span>
      </h2>

      <div className="space-y-2">
        {data.weak_concepts.map((wc) => (
          <div key={wc.concept_id} className="rounded-lg px-3 py-2.5" style={{ backgroundColor: 'var(--color-surface-2)' }}>
            <div className="flex items-center gap-2 mb-1.5">
              <TrendingDown size={14} style={{ color: '#ef4444' }} />
              <span className="text-sm font-medium truncate flex-1">{wc.concept_id.replace(/-/g, ' ')}</span>
              <span className="text-xs font-mono px-1.5 py-0.5 rounded" style={{ backgroundColor: '#ef444420', color: '#ef4444' }}>
                {wc.current_score}分
              </span>
            </div>

            {/* Score trend mini sparkline */}
            {wc.score_trend.length >= 2 && (
              <div className="flex items-end gap-0.5 h-4 mb-1.5">
                {wc.score_trend.map((s, i) => (
                  <div key={i} className="flex-1 rounded-sm" style={{
                    height: `${Math.max(15, s)}%`,
                    backgroundColor: s >= 75 ? '#22c55e' : s >= 50 ? '#f59e0b' : '#ef4444',
                    opacity: 0.6 + (i / wc.score_trend.length) * 0.4,
                  }} />
                ))}
              </div>
            )}

            <div className="flex flex-wrap gap-1 mb-1">
              {wc.reasons.map((r, i) => (
                <span key={i} className="text-xs px-1.5 py-0.5 rounded-full" style={{ backgroundColor: '#ef444410', color: '#ef4444' }}>{r}</span>
              ))}
            </div>

            <div className="flex items-start gap-1.5 text-xs opacity-60">
              <Lightbulb size={11} className="mt-0.5 shrink-0" style={{ color: '#f59e0b' }} />
              <span>{wc.suggestion}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
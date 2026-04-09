import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass, ArrowRight, Link2, Sparkles } from 'lucide-react';

interface DomainRec {
  domain_id: string;
  domain_name: string;
  icon: string;
  color: string;
  score: number;
  reasons: string[];
  cross_link_count: number;
  total_concepts: number;
  avg_difficulty: number;
}

interface RecResponse {
  recommendations: DomainRec[];
  active_domains: { domain_id: string; domain_name: string; mastered: number; learning: number }[];
  total_undiscovered: number;
}

export function DomainRecommendWidget({ limit = 4 }: { limit?: number }) {
  const navigate = useNavigate();
  const [data, setData] = useState<RecResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';
    fetch(`${base}/api/analytics/domain-recommendation?limit=${limit}`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [limit]);

  if (loading) return (
    <section className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="h-5 w-40 rounded bg-white/10 mb-4" />
      <div className="space-y-3">{[1,2,3].map(i => <div key={i} className="h-16 rounded-lg bg-white/5" />)}</div>
    </section>
  );

  if (!data || data.recommendations.length === 0) return null;

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h2 className="text-base font-semibold mb-4 flex items-center gap-2">
        <Compass size={18} style={{ color: '#f59e0b' }} />
        推荐探索领域
        <span className="text-xs font-normal opacity-50 ml-auto">{data.total_undiscovered} 个领域待探索</span>
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {data.recommendations.map((rec) => (
          <button
            key={rec.domain_id}
            onClick={() => navigate(`/domain/${rec.domain_id}`)}
            className="text-left rounded-lg p-3 transition-all hover:scale-[1.02] hover:ring-1"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              borderLeft: `3px solid ${rec.color}`,
              '--tw-ring-color': rec.color,
            } as React.CSSProperties}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">{rec.icon}</span>
              <span className="font-medium text-sm truncate">{rec.domain_name}</span>
              <ArrowRight size={14} className="ml-auto opacity-40 shrink-0" />
            </div>

            <div className="flex items-center gap-3 text-xs opacity-60 mb-2">
              <span>{rec.total_concepts} 概念</span>
              <span>难度 {rec.avg_difficulty}</span>
              {rec.cross_link_count > 0 && (
                <span className="flex items-center gap-1"><Link2 size={10} />{rec.cross_link_count} 关联</span>
              )}
            </div>

            <div className="flex flex-wrap gap-1">
              {rec.reasons.slice(0, 2).map((r, i) => (
                <span key={i} className="text-xs px-1.5 py-0.5 rounded-full flex items-center gap-1"
                  style={{ backgroundColor: `${rec.color}15`, color: rec.color }}>
                  <Sparkles size={9} />{r}
                </span>
              ))}
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}
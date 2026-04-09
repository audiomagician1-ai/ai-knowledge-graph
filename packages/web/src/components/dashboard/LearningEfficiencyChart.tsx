import { useState, useEffect } from 'react';
import { Zap, ArrowUpDown } from 'lucide-react';

interface DomainEfficiency {
  domain_id: string;
  domain_name: string;
  avg_efficiency: number;
  concepts_attempted: number;
  concepts_mastered: number;
  avg_sessions_per_concept: number;
}

interface EfficiencyResponse {
  total_assessed: number;
  domain_efficiency: DomainEfficiency[];
  global: {
    avg_efficiency: number;
    median_efficiency: number;
    total_concepts_assessed: number;
    total_mastered: number;
  };
}

export function LearningEfficiencyChart({ maxDomains = 8 }: { maxDomains?: number }) {
  const [data, setData] = useState<EfficiencyResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';
    fetch(`${base}/api/analytics/learning-efficiency`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <section className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="h-5 w-32 rounded bg-white/10 mb-4" />
      <div className="h-40 rounded bg-white/5" />
    </section>
  );

  if (!data || data.domain_efficiency.length === 0) return null;

  const domains = data.domain_efficiency.slice(0, maxDomains);
  const maxEff = Math.max(1, ...domains.map(d => d.avg_efficiency));

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h2 className="text-base font-semibold mb-1 flex items-center gap-2">
        <Zap size={18} style={{ color: '#22c55e' }} />
        学习效率
      </h2>
      <p className="text-xs opacity-40 mb-4">效率 = 掌握分数 / 学习次数（越高越好）</p>

      {/* Global stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        {[
          { label: '平均效率', value: data.global.avg_efficiency },
          { label: '已评估', value: data.global.total_concepts_assessed },
          { label: '已掌握', value: data.global.total_mastered },
        ].map((s, i) => (
          <div key={i} className="text-center rounded-lg p-2" style={{ backgroundColor: 'var(--color-surface-2)' }}>
            <div className="text-lg font-bold" style={{ color: '#22c55e' }}>{s.value}</div>
            <div className="text-xs opacity-50">{s.label}</div>
          </div>
        ))}
      </div>

      {/* Domain efficiency bars (horizontal) */}
      <div className="space-y-2">
        {domains.map((d) => {
          const pct = (d.avg_efficiency / maxEff) * 100;
          const color = d.avg_efficiency >= 70 ? '#22c55e' : d.avg_efficiency >= 40 ? '#f59e0b' : '#ef4444';
          return (
            <div key={d.domain_id}>
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-xs truncate flex-1">{d.domain_name}</span>
                <span className="text-xs font-mono" style={{ color }}>{d.avg_efficiency}</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-2)' }}>
                  <div className="h-full rounded-full transition-all" style={{ width: `${pct}%`, backgroundColor: color }} />
                </div>
                <span className="text-xs opacity-40 w-16 text-right">
                  <ArrowUpDown size={9} className="inline mr-0.5" />{d.avg_sessions_per_concept}次/概念
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
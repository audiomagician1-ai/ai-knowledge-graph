/**
 * DomainOverviewBatchWidget — Compact grid of all 36 domains with progress.
 * V3.7: Single API call for batch domain stats (replaces N individual calls).
 */
import { useState, useEffect } from 'react';
import { Globe, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface DomainEntry {
  domain_id: string; name: string; icon: string; color: string;
  concepts: number; subdomains: number; milestones: number;
  difficulty: { avg: number; min: number; max: number; };
  progress: { mastered: number; learning: number; not_started: number; pct: number; };
}
interface BatchData {
  domains: DomainEntry[];
  total: number;
  aggregate: { total_concepts: number; total_edges: number; domains_started: number; };
}

export function DomainOverviewBatchWidget() {
  const [data, setData] = useState<BatchData | null>(null);
  const [showAll, setShowAll] = useState(false);
  const nav = useNavigate();

  useEffect(() => {
    fetch('/api/graph/domain-overview-batch')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const displayed = showAll ? data.domains : data.domains.slice(0, 12);
  const { aggregate: agg } = data;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Globe size={16} className="text-cyan-400" />
        <h3 className="text-sm font-semibold">全部领域概览</h3>
        <span className="ml-auto text-xs opacity-40">
          {agg.domains_started}/{data.total} 已开始 · {agg.total_concepts} 概念
        </span>
      </div>

      {/* Domain grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-3">
        {displayed.map(d => (
          <button
            key={d.domain_id}
            onClick={() => nav(`/graph?domain=${d.domain_id}`)}
            className="flex flex-col p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors text-left group"
          >
            <div className="flex items-center gap-1 mb-1">
              {d.icon && <span className="text-sm">{d.icon}</span>}
              <span className="text-[11px] font-medium truncate flex-1">{d.name}</span>
              <ArrowRight size={10} className="opacity-0 group-hover:opacity-40 transition-opacity shrink-0" />
            </div>
            {/* Mini progress bar */}
            <div className="h-1.5 bg-white/5 rounded-full overflow-hidden mb-1">
              <div
                className="h-full rounded-full transition-all"
                style={{
                  width: `${Math.min(100, d.progress.pct)}%`,
                  backgroundColor: d.progress.pct >= 50 ? '#22c55e' : d.progress.pct > 0 ? '#3b82f6' : '#374151',
                }}
              />
            </div>
            <div className="flex justify-between text-[10px] opacity-40">
              <span>{d.progress.mastered}/{d.concepts}</span>
              <span>难度 {d.difficulty.avg}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Show more toggle */}
      {data.domains.length > 12 && (
        <button
          onClick={() => setShowAll(!showAll)}
          className="w-full text-center text-xs text-cyan-400 hover:text-cyan-300 py-1"
        >
          {showAll ? `收起 (显示 12/${data.total})` : `展开全部 ${data.total} 个领域`}
        </button>
      )}
    </div>
  );
}

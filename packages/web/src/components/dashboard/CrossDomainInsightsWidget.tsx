import { useState, useEffect } from 'react';
import { GitBranch, ArrowRight } from 'lucide-react';

interface DomainPair {
  domain_a: string;
  domain_a_name: string;
  domain_b: string;
  domain_b_name: string;
  shared_links: number;
  transfer_score: number;
}

interface Suggestion {
  domain_id: string;
  domain_name: string;
  synergy_score: number;
  reason: string;
}

interface InsightsData {
  domain_pairs: DomainPair[];
  total_cross_links: number;
  active_domains: number;
  suggested_next: Suggestion[];
}

export function CrossDomainInsightsWidget() {
  const [data, setData] = useState<InsightsData | null>(null);

  useEffect(() => {
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    fetch(`${base}/api/analytics/cross-domain-insights`)
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <GitBranch className="w-4 h-4 text-cyan-400" />
        <h3 className="text-sm font-semibold text-white/90">跨域知识关联</h3>
        <span className="text-[10px] text-white/30 ml-auto">{data.total_cross_links} 条跨域链接</span>
      </div>

      {/* Top domain pairs */}
      <div className="space-y-2 mb-3">
        {data.domain_pairs.slice(0, 5).map((p, i) => (
          <div key={i} className="flex items-center gap-2 text-xs">
            <span className="text-white/70 truncate flex-1">{p.domain_a_name}</span>
            <div className="flex items-center gap-1 text-white/30">
              <div className="w-6 h-1 bg-cyan-500/30 rounded" style={{ width: `${Math.min(24, p.shared_links * 2)}px` }} />
              <span className="text-[10px]">{p.shared_links}</span>
            </div>
            <span className="text-white/70 truncate flex-1 text-right">{p.domain_b_name}</span>
          </div>
        ))}
      </div>

      {/* Suggested next domains */}
      {data.suggested_next.length > 0 && (
        <>
          <div className="text-[10px] text-white/40 mb-2 uppercase tracking-wider">推荐探索</div>
          <div className="space-y-1.5">
            {data.suggested_next.slice(0, 3).map((s, i) => (
              <div key={i} className="flex items-center gap-2 bg-cyan-500/10 rounded-lg px-3 py-1.5">
                <ArrowRight className="w-3 h-3 text-cyan-400" />
                <span className="text-xs text-white/80 flex-1">{s.domain_name}</span>
                <span className="text-[10px] text-cyan-300/60">{s.reason}</span>
              </div>
            ))}
          </div>
        </>
      )}

      {data.domain_pairs.length === 0 && (
        <div className="text-xs text-white/30 text-center py-3">开始学习后查看跨域关联</div>
      )}
    </div>
  );
}

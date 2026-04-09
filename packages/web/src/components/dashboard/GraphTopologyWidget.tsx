/**
 * GraphTopologyWidget — Displays domain graph topology insights: hubs, bridges, isolated concepts.
 * V3.0: Backend-powered via /api/graph/relationship-strength/{domain_id}.
 */
import { useState, useEffect } from 'react';
import { useDomainStore } from '@/lib/store/domain';
import { GitBranch, Circle, Link2, AlertTriangle } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface Hub { id: string; name: string; total_degree: number; subdomain: string }
interface Bridge { id: string; name: string; bridge_score: number; cross_subdomains: string[] }
interface SubDensity { subdomain_id: string; concepts: number; density: number }

interface TopologyData {
  domain_id: string;
  hubs: Hub[];
  bridges: Bridge[];
  isolated: { id: string; name: string }[];
  subdomain_density: SubDensity[];
  avg_degree: number;
  total_concepts: number;
  total_edges: number;
}

export function GraphTopologyWidget() {
  const activeDomain = useDomainStore((s) => s.activeDomain);
  const [data, setData] = useState<TopologyData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeDomain) return;
    setLoading(true);
    fetchWithRetry(`${API_BASE}/graph/relationship-strength/${activeDomain}`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [activeDomain]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <GitBranch size={16} style={{ color: 'var(--color-accent)' }} />
          图谱拓扑
        </h3>
        <div className="animate-pulse h-20 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <GitBranch size={16} style={{ color: 'var(--color-accent)' }} />
        图谱拓扑分析
        <span className="text-[10px] font-normal opacity-40 ml-auto">
          {data.total_concepts}概念 · {data.total_edges}边 · 平均度{data.avg_degree}
        </span>
      </h3>

      {/* Hubs */}
      {data.hubs.length > 0 && (
        <div className="mb-3">
          <p className="text-[10px] uppercase tracking-wider opacity-40 mb-1.5 flex items-center gap-1">
            <Circle size={8} /> 核心枢纽 (Top 5)
          </p>
          <div className="space-y-1">
            {data.hubs.slice(0, 5).map((h) => (
              <div key={h.id} className="flex items-center gap-2 text-xs">
                <span className="flex-1 truncate">{h.name}</span>
                <span className="text-[10px] opacity-50 font-mono">{h.total_degree}链接</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Bridges */}
      {data.bridges.length > 0 && (
        <div className="mb-3">
          <p className="text-[10px] uppercase tracking-wider opacity-40 mb-1.5 flex items-center gap-1">
            <Link2 size={8} /> 跨域桥接 (Top 5)
          </p>
          <div className="space-y-1">
            {data.bridges.slice(0, 5).map((b) => (
              <div key={b.id} className="flex items-center gap-2 text-xs">
                <span className="flex-1 truncate">{b.name}</span>
                <span className="text-[10px] opacity-50">{b.bridge_score}子域</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Isolated warning */}
      {data.isolated.length > 0 && (
        <div className="flex items-center gap-2 text-[10px] opacity-50 mt-2">
          <AlertTriangle size={10} className="text-yellow-500" />
          {data.isolated.length} 个孤立概念(无连接)
        </div>
      )}
    </div>
  );
}
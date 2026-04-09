/**
 * ConceptClusterWidget — Shows detected concept clusters (learning modules) in the active domain.
 * V3.1: Backend-powered via /api/graph/concept-clusters/{domain_id}.
 */
import { useState, useEffect } from 'react';
import { useDomainStore } from '@/lib/store/domain';
import { Boxes, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface Gateway { id: string; name: string; external_connections: number }
interface Cluster {
  cluster_id: number;
  size: number;
  density: number;
  avg_difficulty: number;
  difficulty_range: [number, number];
  primary_subdomain: string;
  gateways: Gateway[];
}

interface ClustersData {
  domain_id: string;
  total_clusters: number;
  total_concepts_in_clusters: number;
  clusters: Cluster[];
}

export function ConceptClusterWidget() {
  const activeDomain = useDomainStore((s) => s.activeDomain);
  const [data, setData] = useState<ClustersData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<number | null>(null);

  useEffect(() => {
    if (!activeDomain) return;
    setLoading(true);
    fetchWithRetry(`${API_BASE}/graph/concept-clusters/${activeDomain}?min_cluster_size=3`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [activeDomain]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Boxes size={16} style={{ color: 'var(--color-accent)' }} /> 概念模块
        </h3>
        <div className="animate-pulse h-16 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (!data || data.clusters.length === 0) return null;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Boxes size={16} style={{ color: 'var(--color-accent)' }} />
        概念模块
        <span className="text-[10px] font-normal opacity-40 ml-auto">
          {data.total_clusters}模块 · {data.total_concepts_in_clusters}概念
        </span>
      </h3>

      <div className="space-y-2">
        {data.clusters.slice(0, 6).map((c) => {
          const isOpen = expanded === c.cluster_id;
          return (
            <div key={c.cluster_id} className="rounded-lg p-2.5" style={{ backgroundColor: 'var(--color-surface-2)' }}>
              <button
                className="flex items-center gap-2 w-full text-xs text-left"
                onClick={() => setExpanded(isOpen ? null : c.cluster_id)}
              >
                <span className="flex-1 font-medium truncate">
                  {c.primary_subdomain || `模块 ${c.cluster_id + 1}`}
                </span>
                <span className="text-[10px] opacity-50">{c.size}概念</span>
                <span className="text-[10px] opacity-40">难度{c.avg_difficulty}</span>
                {isOpen ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
              </button>

              {isOpen && (
                <div className="mt-2 pt-2 border-t space-y-1" style={{ borderColor: 'var(--color-border)' }}>
                  <div className="flex gap-3 text-[10px] opacity-50">
                    <span>密度: {(c.density * 100).toFixed(0)}%</span>
                    <span>难度: {c.difficulty_range[0]}-{c.difficulty_range[1]}</span>
                  </div>
                  {c.gateways.length > 0 && (
                    <div className="mt-1">
                      <p className="text-[10px] opacity-40 mb-0.5">入口概念:</p>
                      {c.gateways.slice(0, 3).map((g) => (
                        <div key={g.id} className="flex items-center gap-1 text-[10px] opacity-60">
                          <ExternalLink size={8} />
                          <span className="truncate">{g.name}</span>
                          <span className="opacity-50">({g.external_connections}外链)</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

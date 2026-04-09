import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { Globe, ArrowRight, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface Bridge {
  concept_id: string;
  concept_name: string;
  domain_id: string;
  domain_name: string;
  subdomain_id: string;
  difficulty: number;
  relation_type: string;
  rationale: string;
  direction: 'incoming' | 'outgoing';
}

interface BridgeData {
  concept_id: string;
  bridges: Bridge[];
  total: number;
  domains_connected: string[];
  by_domain: Record<string, Bridge[]>;
}

/**
 * Cross-Domain Bridge Panel — shows related concepts in other knowledge spheres.
 * Integrates into concept detail views or chat idle state.
 */
export function CrossDomainBridge({
  conceptId,
  domainId,
}: {
  conceptId: string;
  domainId: string;
}) {
  const navigate = useNavigate();
  const [data, setData] = useState<BridgeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (!conceptId || !domainId) return;
    setLoading(true);
    fetchWithRetry(
      `${API_BASE}/graph/cross-domain-bridge/${encodeURIComponent(conceptId)}?domain=${encodeURIComponent(domainId)}`
    )
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [conceptId, domainId]);

  if (loading) return <div className="h-16 bg-white/5 rounded-lg animate-pulse" />;
  if (!data || data.total === 0) return null;

  const visibleBridges = expanded ? data.bridges : data.bridges.slice(0, 3);

  return (
    <div className="bg-white/[0.03] border border-white/5 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 border-b border-white/5">
        <Globe size={16} className="text-purple-400" />
        <span className="text-sm font-medium">跨域关联</span>
        <span className="ml-auto text-xs text-gray-500">
          {data.total} 个概念 · {data.domains_connected.length} 个域
        </span>
      </div>

      {/* Bridge list */}
      <div className="divide-y divide-white/5">
        {visibleBridges.map((bridge, i) => (
          <div
            key={`${bridge.domain_id}-${bridge.concept_id}-${i}`}
            className="flex items-center gap-3 px-4 py-2.5 hover:bg-white/[0.04] transition-colors cursor-pointer group"
            onClick={() => navigate(`/domain/${bridge.domain_id}/${bridge.concept_id}`)}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate group-hover:text-blue-300 transition-colors">
                {bridge.concept_name}
              </p>
              <div className="flex items-center gap-2 text-[10px] text-gray-500">
                <span className="text-purple-400/70">{bridge.domain_name}</span>
                <ArrowRight size={8} className="opacity-50" />
                <span>{bridge.relation_type}</span>
                {bridge.rationale && (
                  <>
                    <span>·</span>
                    <span className="truncate max-w-[140px]">{bridge.rationale}</span>
                  </>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] text-gray-600">
                难度 {bridge.difficulty}
              </span>
              <ExternalLink size={12} className="text-gray-600 group-hover:text-blue-400 transition-colors" />
            </div>
          </div>
        ))}
      </div>

      {/* Show more/less */}
      {data.total > 3 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-center gap-1 px-4 py-2 text-xs text-gray-500 hover:text-gray-300 border-t border-white/5 transition-colors"
        >
          {expanded ? (
            <>收起 <ChevronUp size={12} /></>
          ) : (
            <>展开全部 ({data.total}) <ChevronDown size={12} /></>
          )}
        </button>
      )}
    </div>
  );
}

import { useState, useEffect } from 'react';
import { GitCompare, ArrowRight, Link, Minus, Check, X } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { useDomainStore } from '@/lib/store/domain';
import { useGraphStore } from '@/lib/store/graph';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface CompareData {
  concept_a: { id: string; name: string; difficulty: number; subdomain: string; connections: number; prerequisites: string[]; is_milestone: boolean };
  concept_b: { id: string; name: string; difficulty: number; subdomain: string; connections: number; prerequisites: string[]; is_milestone: boolean };
  comparison: {
    directly_connected: boolean;
    shared_connections: string[];
    shared_connection_count: number;
    shared_prerequisites: string[];
    same_subdomain: boolean;
    difficulty_gap: number;
    similarity_score: number;
  };
}

interface ConceptCompareProps {
  conceptA: string;
  conceptB: string;
  onClose?: () => void;
}

/**
 * ConceptCompare — Side-by-side comparison of two concepts.
 *
 * Shows: name, difficulty, connections, prerequisites, and shared metrics.
 */
export function ConceptCompare({ conceptA, conceptB, onClose }: ConceptCompareProps) {
  const [data, setData] = useState<CompareData | null>(null);
  const [loading, setLoading] = useState(true);
  const domainId = useDomainStore((s) => s.activeDomain);

  useEffect(() => {
    if (!conceptA || !conceptB || conceptA === conceptB) {
      setLoading(false);
      return;
    }

    const load = async () => {
      try {
        const res = await fetchWithRetry(
          `${API_BASE}/graph/compare-concepts?concept_a=${encodeURIComponent(conceptA)}&concept_b=${encodeURIComponent(conceptB)}&domain_id=${domainId}`
        );
        if (res.ok) setData(await res.json());
      } catch { /* fail silently */ }
      finally { setLoading(false); }
    };
    load();
  }, [conceptA, conceptB, domainId]);

  if (loading) {
    return (
      <div className="rounded-xl p-4 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <div className="h-4 w-24 rounded" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (!data) return null;

  const { concept_a: a, concept_b: b, comparison: c } = data;

  return (
    <div className="rounded-xl p-4 space-y-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold flex items-center gap-2">
          <GitCompare size={16} style={{ color: 'var(--color-accent)' }} />
          概念对比
        </h3>
        {onClose && (
          <button onClick={onClose} className="p-1 rounded hover:bg-white/10">
            <X size={14} />
          </button>
        )}
      </div>

      {/* Side by side */}
      <div className="grid grid-cols-2 gap-3">
        <ConceptCard name={a.name} difficulty={a.difficulty} connections={a.connections} prerequisites={a.prerequisites.length} isMilestone={a.is_milestone} color="#3b82f6" />
        <ConceptCard name={b.name} difficulty={b.difficulty} connections={b.connections} prerequisites={b.prerequisites.length} isMilestone={b.is_milestone} color="#8b5cf6" />
      </div>

      {/* Comparison metrics */}
      <div className="space-y-2 pt-2 border-t" style={{ borderColor: 'var(--color-border)' }}>
        <MetricRow label="直接连接" value={c.directly_connected ? '是' : '否'} icon={c.directly_connected ? <Check size={12} style={{ color: '#22c55e' }} /> : <Minus size={12} />} />
        <MetricRow label="共同连接" value={`${c.shared_connection_count} 个`} icon={<Link size={12} />} />
        <MetricRow label="共同前置" value={`${c.shared_prerequisites.length} 个`} icon={<ArrowRight size={12} />} />
        <MetricRow label="同一子域" value={c.same_subdomain ? '是' : '否'} icon={c.same_subdomain ? <Check size={12} style={{ color: '#22c55e' }} /> : <Minus size={12} />} />
        <MetricRow label="难度差距" value={`${c.difficulty_gap} 级`} />

        {/* Similarity bar */}
        <div className="pt-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs opacity-50">相似度</span>
            <span className="text-xs font-medium" style={{ color: c.similarity_score > 50 ? '#22c55e' : '#f59e0b' }}>
              {c.similarity_score}%
            </span>
          </div>
          <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-2)' }}>
            <div
              className="h-full rounded-full transition-all"
              style={{
                width: `${c.similarity_score}%`,
                backgroundColor: c.similarity_score > 50 ? '#22c55e' : '#f59e0b',
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function ConceptCard({
  name, difficulty, connections, prerequisites, isMilestone, color,
}: {
  name: string; difficulty: number; connections: number; prerequisites: number; isMilestone: boolean; color: string;
}) {
  return (
    <div className="rounded-lg p-3 space-y-2" style={{ backgroundColor: 'var(--color-surface-0)', borderLeft: `3px solid ${color}` }}>
      <p className="text-xs font-semibold truncate" title={name}>{name}</p>
      <div className="grid grid-cols-2 gap-1 text-[10px] opacity-60">
        <span>难度: {difficulty}/10</span>
        <span>连接: {connections}</span>
        <span>前置: {prerequisites}</span>
        {isMilestone && <span style={{ color: '#f59e0b' }}>⭐ 里程碑</span>}
      </div>
    </div>
  );
}

function MetricRow({ label, value, icon }: { label: string; value: string; icon?: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="opacity-50 flex items-center gap-1">{icon} {label}</span>
      <span className="font-medium">{value}</span>
    </div>
  );
}

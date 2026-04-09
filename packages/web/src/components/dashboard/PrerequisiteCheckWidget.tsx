/**
 * PrerequisiteCheckWidget — Shows prerequisite readiness for recommended next concepts.
 * V3.1: Backend-powered via /api/learning/prerequisite-check/{concept_id}.
 */
import { useState, useEffect } from 'react';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { Shield, CheckCircle, AlertCircle, Circle } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface PrereqItem {
  concept_id: string;
  name: string;
  difficulty: number;
  status: string;
  mastery: number;
}

interface PrereqData {
  concept_id: string;
  concept_name: string;
  readiness_score: number;
  recommendation: 'ready' | 'partially_ready' | 'not_ready';
  total_prerequisites: number;
  mastered_prerequisites: number;
  prerequisites: PrereqItem[];
  suggested_next: PrereqItem[];
}

const REC_COLORS: Record<string, string> = {
  ready: '#22c55e',
  partially_ready: '#f59e0b',
  not_ready: '#ef4444',
};

const REC_LABELS: Record<string, string> = {
  ready: '已就绪',
  partially_ready: '部分就绪',
  not_ready: '未就绪',
};

export function PrerequisiteCheckWidget() {
  const activeDomain = useDomainStore((s) => s.activeDomain);
  const progress = useLearningStore((s) => s.progress);
  const [data, setData] = useState<PrereqData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeDomain) return;
    setLoading(true);
    // Find a concept the user is currently learning or next to learn
    const learning = Object.entries(progress)
      .filter(([, v]) => v.status === 'learning')
      .map(([k]) => k);
    const conceptId = learning[0];
    if (!conceptId) { setData(null); setLoading(false); return; }

    fetchWithRetry(`${API_BASE}/learning/prerequisite-check/${conceptId}`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [activeDomain, progress]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Shield size={16} style={{ color: 'var(--color-accent)' }} /> 前置知识检查
        </h3>
        <div className="animate-pulse h-16 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (!data) return null;

  const color = REC_COLORS[data.recommendation] || '#888';
  const label = REC_LABELS[data.recommendation] || data.recommendation;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Shield size={16} style={{ color: 'var(--color-accent)' }} />
        前置知识检查
        <span className="text-[10px] font-normal ml-auto px-1.5 py-0.5 rounded" style={{ backgroundColor: `${color}20`, color }}>
          {label}
        </span>
      </h3>

      <p className="text-xs opacity-70 mb-2">
        {data.concept_name}
        <span className="opacity-50 ml-2">
          {data.mastered_prerequisites}/{data.total_prerequisites} 前置已掌握
        </span>
      </p>

      {/* Readiness bar */}
      <div className="h-1.5 rounded-full mb-3" style={{ backgroundColor: 'var(--color-surface-2)' }}>
        <div className="h-full rounded-full transition-all" style={{ width: `${data.readiness_score}%`, backgroundColor: color }} />
      </div>

      {/* Prerequisites list */}
      {data.prerequisites.length > 0 && (
        <div className="space-y-1">
          {data.prerequisites.slice(0, 5).map((p) => (
            <div key={p.concept_id} className="flex items-center gap-2 text-xs">
              {p.status === 'mastered' ? (
                <CheckCircle size={12} className="text-green-500 shrink-0" />
              ) : p.status === 'learning' ? (
                <AlertCircle size={12} className="text-yellow-500 shrink-0" />
              ) : (
                <Circle size={12} className="opacity-30 shrink-0" />
              )}
              <span className="flex-1 truncate">{p.name}</span>
              <span className="text-[10px] opacity-40 font-mono">{p.mastery}%</span>
            </div>
          ))}
        </div>
      )}

      {/* Suggested next */}
      {data.suggested_next.length > 0 && (
        <p className="text-[10px] opacity-40 mt-2">
          建议先学: {data.suggested_next.slice(0, 3).map((s) => s.name).join(', ')}
        </p>
      )}
    </div>
  );
}

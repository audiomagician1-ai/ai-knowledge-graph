/**
 * ContentHealthWidget — Dashboard widget showing content quality overview.
 * Displays feedback summary and concepts needing attention.
 * V2.11
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, CheckCircle2, AlertTriangle, ThumbsUp, ChevronRight } from 'lucide-react';

interface ConceptHealth {
  concept_id: string;
  domain_id: string | null;
  total_feedback: number;
  issues: number;
  positive: number;
  unresolved: number;
  health_score: number;
  categories: Record<string, number>;
}

interface HealthData {
  summary: {
    total_feedback: number;
    total_issues: number;
    total_unresolved: number;
    concepts_with_issues: number;
  };
  concepts: ConceptHealth[];
}

const API_BASE = import.meta.env.VITE_API_URL || '';

export function ContentHealthWidget() {
  const navigate = useNavigate();
  const [data, setData] = useState<HealthData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/community/content-health?limit=5`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setData(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="rounded-xl p-5 animate-pulse h-32" style={{ backgroundColor: 'var(--color-surface-1)' }} />;
  if (!data) return null;

  const { summary } = data;
  const hasIssues = summary.total_issues > 0;

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
        <ShieldAlert size={18} style={{ color: hasIssues ? '#f59e0b' : '#22c55e' }} />
        内容健康度
      </h2>

      {/* Summary stats */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-2 rounded-lg" style={{ backgroundColor: 'var(--color-surface-0)' }}>
          <div className="text-lg font-bold" style={{ color: '#3b82f6' }}>{summary.total_feedback}</div>
          <div className="text-[10px]" style={{ color: 'var(--color-text-secondary)' }}>总反馈</div>
        </div>
        <div className="text-center p-2 rounded-lg" style={{ backgroundColor: 'var(--color-surface-0)' }}>
          <div className="text-lg font-bold" style={{ color: summary.total_unresolved > 0 ? '#ef4444' : '#22c55e' }}>
            {summary.total_unresolved}
          </div>
          <div className="text-[10px]" style={{ color: 'var(--color-text-secondary)' }}>待处理</div>
        </div>
        <div className="text-center p-2 rounded-lg" style={{ backgroundColor: 'var(--color-surface-0)' }}>
          <div className="text-lg font-bold" style={{ color: '#22c55e' }}>
            {summary.total_feedback - summary.total_issues}
          </div>
          <div className="text-[10px]" style={{ color: 'var(--color-text-secondary)' }}>好评</div>
        </div>
      </div>

      {/* Concepts needing attention */}
      {data.concepts.length > 0 && (
        <div className="space-y-2">
          <h3 className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>需要关注的概念</h3>
          {data.concepts.slice(0, 5).map(c => (
            <div
              key={c.concept_id}
              onClick={() => c.domain_id && navigate(`/domain/${c.domain_id}/${c.concept_id}`)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer hover:bg-white/5 transition-colors"
              style={{ backgroundColor: 'var(--color-surface-0)' }}
            >
              {c.unresolved > 0
                ? <AlertTriangle size={14} style={{ color: '#f59e0b' }} />
                : <CheckCircle2 size={14} style={{ color: '#22c55e' }} />
              }
              <span className="text-sm flex-1 truncate">{c.concept_id.replace(/-/g, ' ')}</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded" style={{
                backgroundColor: c.health_score >= 70 ? '#22c55e20' : c.health_score >= 40 ? '#f59e0b20' : '#ef444420',
                color: c.health_score >= 70 ? '#22c55e' : c.health_score >= 40 ? '#f59e0b' : '#ef4444',
              }}>
                {c.health_score}
              </span>
              <span className="text-[10px]" style={{ color: 'var(--color-text-tertiary)' }}>
                {c.issues} issue{c.issues !== 1 ? 's' : ''}
              </span>
              <ChevronRight size={12} style={{ color: 'var(--color-text-tertiary)' }} />
            </div>
          ))}
        </div>
      )}

      {/* Empty state */}
      {!hasIssues && (
        <div className="flex items-center gap-2 py-3 text-sm" style={{ color: '#22c55e' }}>
          <ThumbsUp size={16} /> 内容质量良好，暂无问题报告
        </div>
      )}
    </section>
  );
}

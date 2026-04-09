/**
 * OnboardingRecommendWidget — Intelligent first-visit domain recommendations.
 * Shows top beginner-friendly domains with scores, entry concepts, and time estimates.
 * V3.0: Backend-powered recommendations via /api/onboarding/recommended-start.
 */
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass, Star, Clock, ChevronRight, Sparkles } from 'lucide-react';
import {
  fetchRecommendedStart,
  fetchDomainPreview,
  type DomainRecommendation,
  type DomainPreviewResponse,
} from '@/lib/api/onboarding-api';

export function OnboardingRecommendWidget() {
  const navigate = useNavigate();
  const [recs, setRecs] = useState<DomainRecommendation[]>([]);
  const [preview, setPreview] = useState<DomainPreviewResponse | null>(null);
  const [previewId, setPreviewId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendedStart()
      .then((d) => setRecs(d.recommendations.slice(0, 6)))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const openPreview = useCallback((domainId: string) => {
    setPreviewId(domainId);
    setPreview(null);
    fetchDomainPreview(domainId)
      .then(setPreview)
      .catch(() => setPreviewId(null));
  }, []);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Compass size={16} style={{ color: 'var(--color-accent)' }} />
          推荐起点
        </h3>
        <div className="animate-pulse space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
          ))}
        </div>
      </div>
    );
  }

  if (recs.length === 0) return null;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Compass size={16} style={{ color: 'var(--color-accent)' }} />
        推荐起点
      </h3>

      <div className="space-y-2">
        {recs.map((r) => (
          <button
            key={r.domain_id}
            onClick={() => openPreview(r.domain_id)}
            className="w-full flex items-center gap-3 p-2.5 rounded-lg text-left transition-colors hover:brightness-110"
            style={{ backgroundColor: r.color + '15' }}
          >
            <span className="text-lg">{r.icon || '📚'}</span>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium truncate">{r.name}</div>
              <div className="text-[10px] opacity-50 truncate">{r.reason}</div>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <Star size={10} style={{ color: '#fbbf24' }} />
              <span className="text-[10px] font-mono">{r.beginner_score.toFixed(0)}</span>
              <ChevronRight size={12} className="opacity-30" />
            </div>
          </button>
        ))}
      </div>

      {/* Domain Preview Modal */}
      {previewId && (
        <DomainPreviewModal
          domainId={previewId}
          preview={preview}
          color={recs.find((r) => r.domain_id === previewId)?.color || '#6366f1'}
          onClose={() => setPreviewId(null)}
          onStart={() => navigate(`/graph?domain=${previewId}`)}
        />
      )}
    </div>
  );
}

/* ── Domain Preview Modal ─────────────────────────────── */

function DomainPreviewModal({
  domainId,
  preview,
  color,
  onClose,
  onStart,
}: {
  domainId: string;
  preview: DomainPreviewResponse | null;
  color: string;
  onClose: () => void;
  onStart: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0,0,0,0.6)' }}
      onClick={onClose}
    >
      <div
        className="rounded-2xl p-5 max-w-md w-full max-h-[80vh] overflow-y-auto"
        style={{ backgroundColor: 'var(--color-surface-1)' }}
        onClick={(e) => e.stopPropagation()}
      >
        {!preview ? (
          <div className="text-center py-8 opacity-40">
            <Sparkles size={24} className="mx-auto mb-2 animate-spin" />
            <p className="text-xs">加载域预览...</p>
          </div>
        ) : (
          <>
            <h3 className="text-base font-bold mb-1">{domainId.replace(/-/g, ' ')}</h3>
            <div className="flex gap-3 text-[10px] opacity-50 mb-4">
              <span>{preview.total_concepts} 概念</span>
              <span>{preview.total_subdomains} 子域</span>
              <span>≈{preview.estimated_total_hours}h</span>
              <span>难度 {preview.avg_difficulty}</span>
            </div>

            {/* Entry concepts */}
            <p className="text-[10px] uppercase tracking-wider opacity-40 mb-2">入口概念</p>
            <div className="space-y-1 mb-4">
              {preview.entry_concepts.slice(0, 5).map((c) => (
                <div key={c.id} className="flex items-center gap-2 text-xs">
                  <span
                    className="w-1.5 h-1.5 rounded-full shrink-0"
                    style={{ backgroundColor: color }}
                  />
                  <span className="flex-1 truncate">{c.name}</span>
                  <span className="text-[10px] opacity-40">
                    <Clock size={9} className="inline mr-0.5" />
                    {c.estimated_minutes}m
                  </span>
                </div>
              ))}
            </div>

            {/* Difficulty distribution mini bar */}
            <p className="text-[10px] uppercase tracking-wider opacity-40 mb-2">难度分布</p>
            <div className="flex gap-0.5 h-6 mb-4">
              {preview.difficulty_distribution.map((d) => (
                <div
                  key={d.level}
                  className="flex-1 rounded-sm"
                  style={{
                    backgroundColor: color,
                    opacity: d.count > 0 ? 0.2 + (d.count / preview.total_concepts) * 3 : 0.05,
                  }}
                  title={`难度 ${d.level}: ${d.count} 概念`}
                />
              ))}
            </div>

            {/* Subdomains */}
            <p className="text-[10px] uppercase tracking-wider opacity-40 mb-2">子域概览</p>
            <div className="flex flex-wrap gap-1 mb-5">
              {preview.subdomain_summary.slice(0, 8).map((s) => (
                <span
                  key={s.id}
                  className="text-[10px] px-2 py-0.5 rounded-full"
                  style={{ backgroundColor: color + '22', color }}
                >
                  {s.name} ({s.concept_count})
                </span>
              ))}
            </div>

            <button
              onClick={onStart}
              className="w-full py-2.5 rounded-xl text-sm font-semibold text-white transition-transform hover:scale-[1.02]"
              style={{ backgroundColor: color }}
            >
              开始探索
            </button>
          </>
        )}
      </div>
    </div>
  );
}
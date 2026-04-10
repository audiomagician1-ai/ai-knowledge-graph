/**
 * OnboardingRecommendWidget — Intelligent first-visit domain recommendations.
 * Shows top beginner-friendly domains with scores, entry concepts, and time estimates.
 * V3.0: Backend-powered recommendations via /api/onboarding/recommended-start.
 * V4.6: DomainPreviewModal extracted to separate file (200→97L).
 */
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Compass, Star, ChevronRight } from 'lucide-react';
import {
  fetchRecommendedStart,
  fetchDomainPreview,
  type DomainRecommendation,
  type DomainPreviewResponse,
} from '@/lib/api/onboarding-api';
import { DomainPreviewModal } from './DomainPreviewModal';

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
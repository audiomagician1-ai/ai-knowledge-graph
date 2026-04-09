/**
 * AdaptivePathWidget — Shows personalized next learning steps.
 * Fuses FSRS reviews + knowledge gaps + frontier concepts.
 * V2.3 Adaptive Learning Intelligence sprint.
 */
import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { Sparkles, BookOpen, RefreshCw, Clock, Unlock, ChevronRight } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface AdaptiveStep {
  concept_id: string;
  name: string;
  action: 'learn' | 'review' | 'fill_gap';
  priority: number;
  reasons: string[];
  estimated_minutes: number;
  difficulty: number;
  subdomain_id: string;
}

const ACTION_CONFIG = {
  review: { icon: Clock, label: '复习', color: '#f59e0b', bg: '#f59e0b20' },
  fill_gap: { icon: Unlock, label: '补缺', color: '#ef4444', bg: '#ef444420' },
  learn: { icon: BookOpen, label: '学习', color: '#3b82f6', bg: '#3b82f620' },
} as const;

export function AdaptivePathWidget({ maxSteps = 6 }: { maxSteps?: number }) {
  const navigate = useNavigate();
  const activeDomain = useDomainStore((s) => s.activeDomain);
  const [steps, setSteps] = useState<AdaptiveStep[]>([]);
  const [loading, setLoading] = useState(true);
  const [counts, setCounts] = useState({ review: 0, gap: 0, learn: 0 });

  const fetchPath = useCallback(async () => {
    if (!activeDomain) return;
    setLoading(true);
    try {
      const url = `${API_BASE}/learning/adaptive-path/${activeDomain}?limit=${maxSteps}`;
      const res = await fetchWithRetry(url, { retries: 1 });
      if (res.ok) {
        const data = await res.json();
        setSteps(data.steps || []);
        setCounts({
          review: data.review_count || 0,
          gap: data.gap_count || 0,
          learn: data.learn_count || 0,
        });
      }
    } catch { /* offline */ }
    finally { setLoading(false); }
  }, [activeDomain, maxSteps]);

  useEffect(() => { fetchPath(); }, [fetchPath]);

  if (loading) {
    return (
      <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles size={18} style={{ color: '#8b5cf6' }} />
          智能学习路径
        </h2>
        <div className="text-sm opacity-50 mt-2">分析中...</div>
      </section>
    );
  }

  if (steps.length === 0) {
    return (
      <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles size={18} style={{ color: '#8b5cf6' }} />
          智能学习路径
        </h2>
        <div className="text-sm opacity-50 mt-2">选择一个学习域后即可查看个性化路径</div>
      </section>
    );
  }

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Sparkles size={18} style={{ color: '#8b5cf6' }} />
          智能学习路径
        </h2>
        <button onClick={fetchPath} className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
          title="刷新">
          <RefreshCw size={16} className="opacity-50" />
        </button>
      </div>

      {/* Action summary badges */}
      <div className="flex gap-2 mb-3">
        {counts.review > 0 && (
          <span className="text-xs px-2 py-0.5 rounded-full"
            style={{ backgroundColor: ACTION_CONFIG.review.bg, color: ACTION_CONFIG.review.color }}>
            📅 {counts.review} 复习
          </span>
        )}
        {counts.gap > 0 && (
          <span className="text-xs px-2 py-0.5 rounded-full"
            style={{ backgroundColor: ACTION_CONFIG.fill_gap.bg, color: ACTION_CONFIG.fill_gap.color }}>
            🔓 {counts.gap} 补缺
          </span>
        )}
        {counts.learn > 0 && (
          <span className="text-xs px-2 py-0.5 rounded-full"
            style={{ backgroundColor: ACTION_CONFIG.learn.bg, color: ACTION_CONFIG.learn.color }}>
            📖 {counts.learn} 新学
          </span>
        )}
      </div>

      {/* Step list */}
      <div className="space-y-2">
        {steps.map((step, idx) => {
          const cfg = ACTION_CONFIG[step.action];
          const Icon = cfg.icon;
          return (
            <button
              key={step.concept_id}
              onClick={() => navigate(`/learn/${activeDomain}/${step.concept_id}`)}
              className="w-full flex items-center gap-3 p-3 rounded-lg hover:ring-1 transition-all text-left"
              style={{ backgroundColor: 'var(--color-surface-2)' }}
            >
              <div className="flex items-center justify-center w-7 h-7 rounded-full text-xs font-bold flex-shrink-0"
                style={{ backgroundColor: cfg.bg, color: cfg.color }}>
                {idx + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">{step.name}</div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs px-1.5 py-0 rounded"
                    style={{ backgroundColor: cfg.bg, color: cfg.color }}>
                    <Icon size={10} className="inline mr-0.5" />
                    {cfg.label}
                  </span>
                  <span className="text-xs opacity-40">
                    ~{step.estimated_minutes}分钟 · 难度{step.difficulty}
                  </span>
                </div>
                {step.reasons.length > 0 && (
                  <div className="text-xs opacity-40 mt-0.5 truncate">
                    {step.reasons.join(' · ')}
                  </div>
                )}
              </div>
              <ChevronRight size={16} className="opacity-30 flex-shrink-0" />
            </button>
          );
        })}
      </div>
    </section>
  );
}

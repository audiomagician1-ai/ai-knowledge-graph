/**
 * ReviewPriorityWidget — Intelligent review queue with contextual reasons.
 * V3.2: Backend-powered via /api/learning/review-priority.
 */
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { RefreshCw, AlertTriangle, Star, Clock } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface ReviewItem {
  concept_id: string;
  name: string;
  domain_id: string;
  difficulty: number;
  priority_score: number;
  reasons: string[];
  overdue_hours: number;
  stability: number;
  lapses: number;
  downstream_count: number;
  mastery_score: number;
}

export function ReviewPriorityWidget({ limit = 8 }: { limit?: number }) {
  const navigate = useNavigate();
  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchWithRetry(`${API_BASE}/learning/review-priority?limit=${limit}`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then((data) => setItems(data?.items || []))
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, [limit]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <RefreshCw size={16} style={{ color: 'var(--color-accent)' }} /> 复习优先级
        </h3>
        <div className="animate-pulse h-20 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (items.length === 0) return null;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <RefreshCw size={16} style={{ color: 'var(--color-accent)' }} />
        复习优先级
        <span className="text-[10px] font-normal opacity-40 ml-auto">{items.length}项待复习</span>
      </h3>

      <div className="space-y-1.5">
        {items.map((item, idx) => (
          <button
            key={item.concept_id}
            className="w-full flex items-center gap-2 text-xs p-1.5 rounded-lg hover:bg-white/5 transition-colors text-left"
            onClick={() => {
              if (item.domain_id) navigate(`/learn/${item.domain_id}/${item.concept_id}`);
            }}
          >
            <span className="text-[10px] opacity-30 w-4">{idx + 1}</span>
            {item.overdue_hours > 24 ? (
              <AlertTriangle size={12} className="text-red-400 shrink-0" />
            ) : item.downstream_count > 2 ? (
              <Star size={12} className="text-yellow-400 shrink-0" />
            ) : (
              <Clock size={12} className="opacity-30 shrink-0" />
            )}
            <span className="flex-1 truncate">{item.name}</span>
            <span className="text-[10px] opacity-40 font-mono shrink-0">{item.priority_score}分</span>
          </button>
        ))}
      </div>

      {items.length > 0 && items[0].reasons.length > 0 && (
        <p className="text-[10px] opacity-35 mt-2 italic">
          最优先: {items[0].reasons[0]}
        </p>
      )}
    </div>
  );
}

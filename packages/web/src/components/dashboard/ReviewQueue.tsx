/**
 * ReviewQueue — Shows concepts due for FSRS spaced repetition review.
 * Sorted by urgency (most overdue first). Integrated into Dashboard.
 * V2.3 Adaptive Learning Intelligence sprint.
 */
import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { Clock, AlertTriangle, ChevronRight, RefreshCw } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface DueItem {
  concept_id: string;
  status: string;
  mastery_score: number;
  fsrs_stability: number;
  fsrs_difficulty: number;
  overdue_days: number;
  fsrs_reps: number;
  fsrs_lapses: number;
}

export function ReviewQueue({ maxItems = 8 }: { maxItems?: number }) {
  const navigate = useNavigate();
  const activeDomain = useDomainStore((s) => s.activeDomain);
  const [items, setItems] = useState<DueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchDue = useCallback(async () => {
    setLoading(true);
    setError(false);
    try {
      const url = `${API_BASE}/learning/due?limit=${maxItems}&domain=${activeDomain || ''}`;
      const res = await fetchWithRetry(url, { retries: 1 });
      if (res.ok) {
        const data = await res.json();
        setItems(data.items || []);
      } else {
        setError(true);
      }
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, [activeDomain, maxItems]);

  useEffect(() => {
    fetchDue();
  }, [fetchDue]);

  if (loading) {
    return (
      <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Clock size={18} style={{ color: '#f59e0b' }} />
          复习队列
        </h2>
        <div className="text-sm opacity-50">加载中...</div>
      </section>
    );
  }

  if (error || items.length === 0) {
    return (
      <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Clock size={18} style={{ color: '#f59e0b' }} />
          复习队列
        </h2>
        <div className="text-sm opacity-50 flex items-center gap-2">
          {error ? '无法加载复习数据' : '🎉 暂无待复习概念，继续学习新知识吧！'}
          {error && (
            <button onClick={fetchDue} className="p-1 rounded hover:bg-white/10">
              <RefreshCw size={14} />
            </button>
          )}
        </div>
      </section>
    );
  }

  const urgentCount = items.filter((i) => i.overdue_days >= 3).length;

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Clock size={18} style={{ color: '#f59e0b' }} />
          复习队列
          <span className="text-sm font-normal px-2 py-0.5 rounded-full"
            style={{ backgroundColor: '#f59e0b20', color: '#f59e0b' }}>
            {items.length} 待复习
          </span>
          {urgentCount > 0 && (
            <span className="text-sm font-normal px-2 py-0.5 rounded-full"
              style={{ backgroundColor: '#ef444420', color: '#ef4444' }}>
              <AlertTriangle size={12} className="inline mr-1" />
              {urgentCount} 紧急
            </span>
          )}
        </h2>
        <button onClick={fetchDue} className="p-1.5 rounded-lg hover:bg-white/10 transition-colors"
          title="刷新">
          <RefreshCw size={16} className="opacity-50" />
        </button>
      </div>

      <div className="space-y-2">
        {items.map((item) => {
          const urgency = item.overdue_days >= 7 ? 'critical' :
            item.overdue_days >= 3 ? 'warning' : 'normal';
          const urgencyColor = urgency === 'critical' ? '#ef4444' :
            urgency === 'warning' ? '#f59e0b' : '#3b82f6';

          return (
            <button
              key={item.concept_id}
              onClick={() => navigate(`/learn/${activeDomain}/${item.concept_id}`)}
              className="w-full flex items-center gap-3 p-3 rounded-lg hover:ring-1 transition-all text-left"
              style={{
                backgroundColor: 'var(--color-surface-2)',
                borderLeft: `3px solid ${urgencyColor}`,
              }}
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate">
                  {item.concept_id.replace(/-/g, ' ')}
                </div>
                <div className="flex gap-3 text-xs opacity-50 mt-0.5">
                  <span>稳定性 {item.fsrs_stability}d</span>
                  <span>复习 {item.fsrs_reps}次</span>
                  {item.overdue_days > 0 && (
                    <span style={{ color: urgencyColor }}>
                      逾期 {item.overdue_days}天
                    </span>
                  )}
                </div>
              </div>
              <ChevronRight size={16} className="opacity-30 flex-shrink-0" />
            </button>
          );
        })}
      </div>
    </section>
  );
}

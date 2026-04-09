/**
 * NextMilestonesWidget — Shows upcoming achievements and milestones.
 * V3.3: Backend-powered via /api/analytics/next-milestones.
 */
import { useState, useEffect } from 'react';
import { Target } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface Milestone {
  type: string;
  label: string;
  current: number;
  target: number;
  remaining: number;
  progress_pct: number;
  badge: string;
}

export function NextMilestonesWidget({ limit = 5 }: { limit?: number }) {
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchWithRetry(`${API_BASE}/analytics/next-milestones?limit=${limit}`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then((data) => setMilestones(data?.milestones || []))
      .catch(() => setMilestones([]))
      .finally(() => setLoading(false));
  }, [limit]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Target size={16} style={{ color: 'var(--color-accent)' }} /> 即将达成
        </h3>
        <div className="animate-pulse h-16 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (milestones.length === 0) return null;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Target size={16} style={{ color: 'var(--color-accent)' }} />
        即将达成
      </h3>

      <div className="space-y-2.5">
        {milestones.map((m, i) => (
          <div key={i} className="flex items-center gap-2">
            <span className="text-base">{m.badge}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-xs truncate">{m.label}</span>
                <span className="text-[10px] opacity-40 font-mono shrink-0 ml-2">
                  还差{m.remaining}
                </span>
              </div>
              <div className="h-1 rounded-full" style={{ backgroundColor: 'var(--color-surface-2)' }}>
                <div className="h-full rounded-full transition-all" style={{
                  width: `${Math.min(100, m.progress_pct)}%`,
                  backgroundColor: m.progress_pct > 80 ? '#22c55e' : m.progress_pct > 50 ? '#f59e0b' : 'var(--color-accent)',
                }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

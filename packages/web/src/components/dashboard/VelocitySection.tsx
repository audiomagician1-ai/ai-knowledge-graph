import { useEffect, useState } from 'react';
import { Zap } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface VelocityData {
  days: number;
  daily: Array<{ date: string; assessments: number; concepts_started: number; mastered: number }>;
  summary: { total_assessments: number; total_concepts_started: number; active_days: number };
}

/** Learning Velocity section — fetches from Analytics API */
export function VelocitySection() {
  const [velocity, setVelocity] = useState<VelocityData | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetchWithRetry(`${API_BASE}/analytics/learning-velocity?days=14`, { retries: 1 });
        if (res.ok && !cancelled) setVelocity(await res.json());
      } catch { /* offline */ }
    })();
    return () => { cancelled = true; };
  }, []);

  if (!velocity || velocity.summary.total_assessments === 0) return null;

  const maxVal = Math.max(1, ...velocity.daily.map((d) => d.assessments + d.concepts_started));

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
        <Zap size={18} style={{ color: '#8b5cf6' }} />
        学习节奏 (14天)
      </h2>
      <div className="flex gap-3 text-xs opacity-60 mb-4">
        <span>活跃天数: {velocity.summary.active_days}</span>
        <span>·</span>
        <span>评估 {velocity.summary.total_assessments} 次</span>
        <span>·</span>
        <span>开始 {velocity.summary.total_concepts_started} 个概念</span>
      </div>
      <div className="flex items-end gap-1 h-20">
        {velocity.daily.map((day) => {
          const total = day.assessments + day.concepts_started;
          const height = (total / maxVal) * 100;
          const label = day.date.slice(5);
          return (
            <div key={day.date} className="flex-1 flex flex-col items-center gap-0.5">
              {total > 0 && <span className="text-[9px] opacity-40">{total}</span>}
              <div
                className="w-full rounded-t"
                title={`${day.date}: ${day.assessments} 评估, ${day.concepts_started} 开始`}
                style={{
                  height: `${Math.max(2, height)}%`,
                  backgroundColor: total > 0 ? '#8b5cf6' : 'var(--color-surface-3)',
                  opacity: total > 0 ? 0.8 : 0.3,
                  transition: 'height 0.3s',
                }}
              />
              <span className="text-[8px] opacity-30">{label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}
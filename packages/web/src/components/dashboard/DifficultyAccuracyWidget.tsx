/**
 * DifficultyAccuracyWidget — Seed difficulty vs actual performance calibration.
 * V3.2: Backend-powered via existing /api/analytics/difficulty-calibration.
 */
import { useState, useEffect } from 'react';
import { useDomainStore } from '@/lib/store/domain';
import { BarChart3, ArrowUp, ArrowDown } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface CalibrationItem {
  concept_id: string; name: string; seed_difficulty: number;
  actual_score: number; gap: number; miscalibrated: boolean;
  signal?: string; suggestion?: string;
}

interface CalibData {
  domain_id: string;
  calibration: CalibrationItem[];
  total_assessed: number;
  miscalibrated_count: number;
  difficulty_summary: { difficulty: number; count: number; avg_score: number; mastery_rate: number }[];
}

export function DifficultyAccuracyWidget() {
  const activeDomain = useDomainStore((s) => s.activeDomain);
  const [data, setData] = useState<CalibData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!activeDomain) return;
    setLoading(true);
    fetchWithRetry(`${API_BASE}/analytics/difficulty-calibration?domain_id=${activeDomain}`, { retries: 1 })
      .then((r) => r.ok ? r.json() : null)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [activeDomain]);

  if (loading) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <BarChart3 size={16} style={{ color: 'var(--color-accent)' }} /> 难度校准
        </h3>
        <div className="animate-pulse h-16 rounded-lg" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (!data || data.total_assessed === 0) return null;

  const miscalibrated = data.calibration.filter((c) => c.miscalibrated).slice(0, 5);

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <BarChart3 size={16} style={{ color: 'var(--color-accent)' }} />
        难度校准
        <span className="text-[10px] font-normal opacity-40 ml-auto">
          {data.miscalibrated_count}/{data.total_assessed} 偏差
        </span>
      </h3>

      {/* Difficulty summary bars */}
      {data.difficulty_summary.length > 0 && (
        <div className="flex items-end gap-0.5 h-12 mb-3">
          {data.difficulty_summary.map((d) => {
            const h = Math.max(4, d.mastery_rate);
            const color = d.mastery_rate > 60 ? '#22c55e' : d.mastery_rate > 30 ? '#f59e0b' : '#ef4444';
            return (
              <div key={d.difficulty} className="flex-1 flex flex-col items-center">
                <div className="w-full rounded-t" style={{ height: `${h}%`, backgroundColor: color, minHeight: 2 }} />
                <span className="text-[8px] opacity-30 mt-0.5">{d.difficulty}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Miscalibrated items */}
      {miscalibrated.length > 0 && (
        <div className="space-y-1">
          {miscalibrated.map((c) => (
            <div key={c.concept_id} className="flex items-center gap-2 text-[10px]">
              {c.signal === 'easier_than_labeled' ? (
                <ArrowUp size={10} className="text-green-400 shrink-0" />
              ) : (
                <ArrowDown size={10} className="text-red-400 shrink-0" />
              )}
              <span className="flex-1 truncate opacity-60">{c.name}</span>
              <span className="opacity-40 font-mono">D{c.seed_difficulty}→{c.actual_score}分</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

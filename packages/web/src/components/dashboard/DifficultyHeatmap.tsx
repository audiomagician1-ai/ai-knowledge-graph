/**
 * DifficultyHeatmap — Visual grid showing concept difficulty distribution per domain.
 * Displays a row per domain, columns for difficulty levels 1-10.
 * Cell intensity = number of concepts at that difficulty.
 */
import { useMemo, useEffect, useState } from 'react';
import { useDomainStore } from '@/lib/store/domain';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { Thermometer } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';
const DIFF_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

interface DomainDifficulty {
  id: string;
  name: string;
  color: string;
  distribution: number[]; // counts for difficulty 1-10
  total: number;
}

export function DifficultyHeatmap() {
  const domains = useDomainStore((s) => s.domains);
  const [data, setData] = useState<DomainDifficulty[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetchWithRetry(`${API_BASE}/graph/stats/global`);
        if (!res.ok) return;
        const json = await res.json();
        // For each domain, fetch topology to get difficulty distribution
        const results: DomainDifficulty[] = [];
        const topDomains = (json.domains || [])
          .sort((a: { concepts: number }, b: { concepts: number }) => b.concepts - a.concepts)
          .slice(0, 8);

        for (const d of topDomains) {
          try {
            const topoRes = await fetchWithRetry(`${API_BASE}/graph/topology/${d.id}`);
            if (!topoRes.ok) continue;
            const topo = await topoRes.json();
            const dist = new Array(10).fill(0);
            // Count difficulties from subdomain stats
            const concepts = topo.total_concepts || 0;
            // Use avg_difficulty per subdomain to estimate distribution
            for (const [, sub] of Object.entries(topo.subdomains || {})) {
              const s = sub as { total: number; avg_difficulty: number };
              const bucket = Math.min(9, Math.max(0, Math.round(s.avg_difficulty) - 1));
              dist[bucket] += s.total;
            }
            results.push({
              id: d.id,
              name: d.name,
              color: d.color || '#6366f1',
              distribution: dist,
              total: concepts,
            });
          } catch { /* skip domain */ }
        }
        setData(results);
      } catch { /* fail silently */ }
      finally { setLoading(false); }
    };
    load();
  }, []);

  const maxCount = useMemo(() => {
    let max = 1;
    for (const d of data) {
      for (const v of d.distribution) {
        if (v > max) max = v;
      }
    }
    return max;
  }, [data]);

  if (loading) {
    return (
      <div className="rounded-xl p-4 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <div className="h-4 w-32 rounded" style={{ backgroundColor: 'var(--color-surface-2)' }} />
      </div>
    );
  }

  if (data.length === 0) return null;

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Thermometer size={16} style={{ color: 'var(--color-accent)' }} />
        难度分布热力图
      </h3>

      {/* Header row: difficulty levels */}
      <div className="flex items-center gap-0.5 mb-1 pl-20">
        {DIFF_LEVELS.map((d) => (
          <div key={d} className="w-6 text-center text-[9px] opacity-40">
            {d}
          </div>
        ))}
      </div>

      {/* Domain rows */}
      <div className="space-y-1">
        {data.map((d) => (
          <div key={d.id} className="flex items-center gap-1">
            <div className="w-20 text-[10px] truncate opacity-60 text-right pr-1" title={d.name}>
              {d.name.slice(0, 10)}
            </div>
            <div className="flex gap-0.5">
              {d.distribution.map((count, i) => {
                const intensity = count / maxCount;
                return (
                  <div
                    key={i}
                    className="w-6 h-5 rounded-sm transition-colors"
                    style={{
                      backgroundColor: count > 0
                        ? `color-mix(in srgb, ${d.color} ${Math.round(20 + intensity * 80)}%, transparent)`
                        : 'var(--color-surface-2)',
                    }}
                    title={`${d.name}: 难度${i + 1} — ${count}个概念`}
                  />
                );
              })}
            </div>
            <span className="text-[9px] opacity-30 ml-1">{d.total}</span>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-3 mt-3 justify-center text-[9px] opacity-40">
        <span>← 简单</span>
        <div className="flex gap-0.5">
          {[0.2, 0.4, 0.6, 0.8, 1].map((v, i) => (
            <div
              key={i}
              className="w-4 h-3 rounded-sm"
              style={{ backgroundColor: `color-mix(in srgb, var(--color-accent) ${Math.round(v * 100)}%, transparent)` }}
            />
          ))}
        </div>
        <span>困难 →</span>
      </div>
    </div>
  );
}

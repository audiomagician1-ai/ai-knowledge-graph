/**
 * DomainRadar — SVG radar chart showing mastery distribution across studied domains.
 * Pure SVG implementation, no external chart library needed.
 */
import { useMemo, useEffect, useState } from 'react';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { Radar } from 'lucide-react';
import { RadarSVG, type RadarPoint } from './RadarSVG';

export function DomainRadar() {
  const domains = useDomainStore((s) => s.domains);
  const progress = useLearningStore((s) => s.progress);
  const [allProgress, setAllProgress] = useState<Record<string, Record<string, { status: string }>>>({});

  useEffect(() => {
    const result: typeof allProgress = {};
    for (const d of domains) {
      try {
        const key = `akg-learning:${d.id}`;
        const raw = localStorage.getItem(key);
        if (raw) { const parsed = JSON.parse(raw); result[d.id] = parsed?.progress || {}; }
      } catch { /* skip */ }
    }
    const activeDomain = useDomainStore.getState().activeDomain;
    if (Object.keys(progress).length > 0) {
      result[activeDomain] = Object.fromEntries(Object.entries(progress).map(([id, p]) => [id, { status: p.status }]));
    }
    setAllProgress(result);
  }, [domains, progress]);

  const points: RadarPoint[] = useMemo(() => {
    if (!domains?.length) return [];
    const results: RadarPoint[] = [];
    for (const d of domains) {
      const dp = allProgress[d.id];
      if (!dp) continue;
      const entries = Object.values(dp);
      const mastered = entries.filter((e) => e.status === 'mastered').length;
      const touched = entries.filter((e) => e.status === 'mastered' || e.status === 'learning').length;
      if (touched === 0) continue;
      const total = d.stats?.total_concepts || entries.length;
      const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
      results.push({ label: (d.name || d.id).slice(0, 8), value: pct, color: d.color || '#6366f1', domainId: d.id });
    }
    results.sort((a, b) => b.value - a.value);
    return results.slice(0, 8);
  }, [domains, allProgress]);

  if (points.length < 3) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Radar size={16} style={{ color: 'var(--color-accent)' }} />
          掌握度雷达
        </h3>
        <p className="text-xs opacity-40 text-center py-6">开始学习3个以上领域后解锁雷达图</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Radar size={16} style={{ color: 'var(--color-accent)' }} />
        掌握度雷达
      </h3>
      <div className="flex justify-center"><RadarSVG points={points} /></div>
      <div className="flex flex-wrap gap-2 mt-3 justify-center">
        {points.map((p) => (
          <span key={p.domainId} className="text-[10px] px-2 py-0.5 rounded-full" style={{ backgroundColor: p.color + '22', color: p.color }}>
            {p.label} {p.value}%
          </span>
        ))}
      </div>
    </div>
  );
}

/**
 * DomainRadar — SVG radar chart showing mastery distribution across studied domains.
 * Pure SVG implementation, no external chart library needed.
 */
import { useMemo, useEffect, useState } from 'react';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { Radar } from 'lucide-react';

const SIZE = 240;
const CENTER = SIZE / 2;
const RADIUS = 90;
const RINGS = 4;

interface RadarPoint {
  label: string;
  value: number; // 0-100
  color: string;
  domainId: string;
}

export function DomainRadar() {
  const domains = useDomainStore((s) => s.domains);
  const progress = useLearningStore((s) => s.progress);
  const [allProgress, setAllProgress] = useState<Record<string, Record<string, { status: string }>>>({});

  // Load per-domain progress from localStorage (same pattern as DashboardPage)
  useEffect(() => {
    const result: typeof allProgress = {};
    for (const d of domains) {
      try {
        const key = `akg-learning:${d.id}`;
        const raw = localStorage.getItem(key);
        if (raw) {
          const parsed = JSON.parse(raw);
          result[d.id] = parsed?.progress || {};
        }
      } catch { /* skip */ }
    }
    // Include current domain from store
    const activeDomain = useDomainStore.getState().activeDomain;
    if (Object.keys(progress).length > 0) {
      result[activeDomain] = Object.fromEntries(
        Object.entries(progress).map(([id, p]) => [id, { status: p.status }])
      );
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
      results.push({
        label: (d.name || d.id).slice(0, 8),
        value: pct,
        color: d.color || '#6366f1',
        domainId: d.id,
      });
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

  const n = points.length;
  const angleStep = (2 * Math.PI) / n;

  const getXY = (i: number, r: number): [number, number] => {
    const angle = -Math.PI / 2 + i * angleStep;
    return [CENTER + r * Math.cos(angle), CENTER + r * Math.sin(angle)];
  };

  // Grid rings
  const rings = Array.from({ length: RINGS }, (_, i) => {
    const r = (RADIUS / RINGS) * (i + 1);
    const pts = Array.from({ length: n }, (_, j) => getXY(j, r));
    return pts.map(([x, y]) => `${x},${y}`).join(' ');
  });

  // Axis lines
  const axes = Array.from({ length: n }, (_, i) => getXY(i, RADIUS));

  // Data polygon
  const dataPoints = points.map((p, i) => {
    const r = (p.value / 100) * RADIUS;
    return getXY(i, Math.max(r, 4)); // min 4px so 0% still visible
  });
  const dataPath = dataPoints.map(([x, y]) => `${x},${y}`).join(' ');

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Radar size={16} style={{ color: 'var(--color-accent)' }} />
        掌握度雷达
      </h3>
      <div className="flex justify-center">
        <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
          {/* Grid rings */}
          {rings.map((pts, i) => (
            <polygon
              key={`ring-${i}`}
              points={pts}
              fill="none"
              stroke="var(--color-border)"
              strokeWidth={0.5}
              opacity={0.3 + i * 0.1}
            />
          ))}

          {/* Axis lines */}
          {axes.map(([x, y], i) => (
            <line
              key={`axis-${i}`}
              x1={CENTER} y1={CENTER}
              x2={x} y2={y}
              stroke="var(--color-border)"
              strokeWidth={0.5}
              opacity={0.4}
            />
          ))}

          {/* Data polygon */}
          <polygon
            points={dataPath}
            fill="var(--color-accent)"
            fillOpacity={0.15}
            stroke="var(--color-accent)"
            strokeWidth={1.5}
          />

          {/* Data dots */}
          {dataPoints.map(([x, y], i) => (
            <circle
              key={`dot-${i}`}
              cx={x} cy={y} r={3}
              fill={points[i].color}
              stroke="var(--color-surface-0)"
              strokeWidth={1}
            />
          ))}

          {/* Labels */}
          {points.map((p, i) => {
            const [x, y] = getXY(i, RADIUS + 18);
            const anchor = x < CENTER - 5 ? 'end' : x > CENTER + 5 ? 'start' : 'middle';
            return (
              <text
                key={`label-${i}`}
                x={x} y={y}
                textAnchor={anchor}
                dominantBaseline="central"
                fill="currentColor"
                opacity={0.6}
                fontSize={9}
              >
                {p.label}
              </text>
            );
          })}

          {/* Center percentage ring labels */}
          {[25, 50, 75, 100].map((pct, i) => {
            const r = (pct / 100) * RADIUS;
            return (
              <text
                key={`pct-${i}`}
                x={CENTER + 2} y={CENTER - r - 1}
                fill="currentColor"
                opacity={0.25}
                fontSize={7}
              >
                {pct}%
              </text>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-2 mt-3 justify-center">
        {points.map((p) => (
          <span
            key={p.domainId}
            className="text-[10px] px-2 py-0.5 rounded-full"
            style={{ backgroundColor: p.color + '22', color: p.color }}
          >
            {p.label} {p.value}%
          </span>
        ))}
      </div>
    </div>
  );
}

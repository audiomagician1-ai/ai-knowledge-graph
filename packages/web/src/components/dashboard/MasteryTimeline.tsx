import { useState, useEffect } from 'react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { TrendingUp, Clock } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface DataPoint {
  score: number;
  mastered: boolean;
  date: string;
  time: string;
}

interface TimelineData {
  concept_id: string;
  data_points: DataPoint[];
  total_sessions: number;
  improvement: number;
  first_seen: string | null;
  last_seen: string | null;
  current: { status: string; mastery_score: number; sessions: number };
}

/**
 * SVG line chart showing mastery progression for a concept.
 * Compact design — integrable into chat idle view or concept details.
 */
export function MasteryTimeline({ conceptId }: { conceptId: string }) {
  const [data, setData] = useState<TimelineData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!conceptId) return;
    setLoading(true);
    fetchWithRetry(`${API_BASE}/analytics/mastery-timeline/${encodeURIComponent(conceptId)}`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [conceptId]);

  if (loading) return <div className="h-24 bg-white/5 rounded-lg animate-pulse" />;
  if (!data || data.data_points.length === 0) return null;

  const points = data.data_points;
  const W = 240;
  const H = 80;
  const PAD = { t: 8, r: 8, b: 20, l: 28 };
  const plotW = W - PAD.l - PAD.r;
  const plotH = H - PAD.t - PAD.b;

  // Scale
  const maxScore = Math.max(100, ...points.map((p) => p.score));
  const xStep = points.length > 1 ? plotW / (points.length - 1) : plotW / 2;
  const toX = (i: number) => PAD.l + i * xStep;
  const toY = (s: number) => PAD.t + plotH - (s / maxScore) * plotH;

  // SVG path
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${toX(i).toFixed(1)},${toY(p.score).toFixed(1)}`).join(' ');

  // Gradient area
  const areaD = `${pathD} L${toX(points.length - 1).toFixed(1)},${(PAD.t + plotH).toFixed(1)} L${PAD.l},${(PAD.t + plotH).toFixed(1)} Z`;

  const improvementColor = data.improvement >= 0 ? 'text-green-400' : 'text-red-400';

  return (
    <div className="bg-white/[0.03] border border-white/5 rounded-lg p-3 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <TrendingUp size={14} />
          <span>掌握度变化</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className={improvementColor}>
            {data.improvement >= 0 ? '+' : ''}{data.improvement}
          </span>
          <span className="text-gray-500">·</span>
          <span className="text-gray-500">{data.total_sessions} 次</span>
        </div>
      </div>

      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 80 }}>
        {/* Y-axis labels */}
        <text x={PAD.l - 4} y={PAD.t + 4} textAnchor="end" className="fill-gray-600 text-[8px]">100</text>
        <text x={PAD.l - 4} y={PAD.t + plotH / 2 + 2} textAnchor="end" className="fill-gray-600 text-[8px]">50</text>
        <text x={PAD.l - 4} y={PAD.t + plotH + 2} textAnchor="end" className="fill-gray-600 text-[8px]">0</text>

        {/* Grid lines */}
        <line x1={PAD.l} y1={toY(75)} x2={W - PAD.r} y2={toY(75)} stroke="rgba(255,255,255,0.05)" strokeDasharray="2" />
        <line x1={PAD.l} y1={toY(50)} x2={W - PAD.r} y2={toY(50)} stroke="rgba(255,255,255,0.05)" strokeDasharray="2" />

        {/* Mastery threshold line */}
        <line x1={PAD.l} y1={toY(75)} x2={W - PAD.r} y2={toY(75)} stroke="rgba(234,179,8,0.2)" strokeDasharray="4" />

        {/* Area fill */}
        <defs>
          <linearGradient id={`mt-grad-${conceptId}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgb(59,130,246)" stopOpacity="0.3" />
            <stop offset="100%" stopColor="rgb(59,130,246)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={areaD} fill={`url(#mt-grad-${conceptId})`} />

        {/* Line */}
        <path d={pathD} fill="none" stroke="rgb(59,130,246)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />

        {/* Data points */}
        {points.map((p, i) => (
          <circle
            key={i}
            cx={toX(i)}
            cy={toY(p.score)}
            r={p.mastered ? 3 : 2}
            fill={p.mastered ? 'rgb(234,179,8)' : 'rgb(59,130,246)'}
            stroke="rgb(17,24,39)"
            strokeWidth="1"
          />
        ))}

        {/* X-axis dates (first and last only) */}
        {points.length > 0 && (
          <>
            <text x={toX(0)} y={H - 2} textAnchor="start" className="fill-gray-600 text-[7px]">{points[0].date.slice(5)}</text>
            {points.length > 1 && (
              <text x={toX(points.length - 1)} y={H - 2} textAnchor="end" className="fill-gray-600 text-[7px]">{points[points.length - 1].date.slice(5)}</text>
            )}
          </>
        )}
      </svg>

      {data.first_seen && (
        <div className="flex items-center gap-1 text-[10px] text-gray-500">
          <Clock size={10} />
          <span>首次: {data.first_seen} → 最近: {data.last_seen}</span>
        </div>
      )}
    </div>
  );
}

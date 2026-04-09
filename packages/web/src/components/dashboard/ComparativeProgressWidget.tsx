/**
 * ComparativeProgressWidget — Week-over-week domain progress comparison.
 * V3.5: Shows learning trend arrows, delta badges, and WoW summary.
 */
import { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

interface DomainWoW {
  domain_id: string; domain_name: string; total_concepts: number; mastered: number;
  progress_pct: number;
  this_week: { events: number; mastered: number; avg_score: number };
  last_week: { events: number; mastered: number; avg_score: number };
  delta: { events: number; mastered: number; avg_score: number };
  trend: 'up' | 'down' | 'stable';
}
interface Summary {
  active_domains: number; this_week_events: number; last_week_events: number;
  events_delta: number; this_week_mastered: number; last_week_mastered: number;
  mastered_delta: number; overall_trend: 'up' | 'down' | 'stable';
}

export function ComparativeProgressWidget() {
  const [domains, setDomains] = useState<DomainWoW[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);

  useEffect(() => {
    fetch('/api/analytics/comparative-progress')
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) { setDomains(d.domains || []); setSummary(d.summary); } })
      .catch(() => {});
  }, []);

  if (!summary) return null;

  const TrendIcon = summary.overall_trend === 'up' ? TrendingUp : summary.overall_trend === 'down' ? TrendingDown : Minus;
  const trendColor = summary.overall_trend === 'up' ? 'text-emerald-400' : summary.overall_trend === 'down' ? 'text-red-400' : 'text-gray-400';

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Activity size={16} className="text-cyan-400" />
        <h3 className="text-sm font-semibold">周度对比</h3>
        <span className={`ml-auto flex items-center gap-1 text-xs ${trendColor}`}>
          <TrendIcon size={12} /> {summary.overall_trend === 'up' ? '进步' : summary.overall_trend === 'down' ? '下降' : '持平'}
        </span>
      </div>

      {/* Global summary */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <SummaryCard label="本周事件" value={summary.this_week_events} delta={summary.events_delta} />
        <SummaryCard label="本周掌握" value={summary.this_week_mastered} delta={summary.mastered_delta} />
      </div>

      {/* Domain rows */}
      {domains.length > 0 ? (
        <div className="space-y-2">
          {domains.slice(0, 8).map(d => (
            <div key={d.domain_id} className="flex items-center gap-2 p-2 bg-white/5 rounded-lg">
              <DomainTrendIcon trend={d.trend} />
              <div className="flex-1 min-w-0">
                <div className="text-xs truncate">{d.domain_name}</div>
                <div className="flex items-center gap-2 text-[10px] opacity-40 mt-0.5">
                  <span>{d.progress_pct}% 掌握</span>
                  <span>本周 {d.this_week.events} 次</span>
                </div>
              </div>
              <div className="text-right shrink-0">
                <DeltaBadge value={d.delta.events} label="次" />
                {d.delta.avg_score !== 0 && (
                  <div className="text-[10px] opacity-40 mt-0.5">
                    均分 {d.delta.avg_score > 0 ? '+' : ''}{d.delta.avg_score}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center text-xs opacity-30 py-4">暂无活跃领域数据</div>
      )}
    </div>
  );
}

function SummaryCard({ label, value, delta }: { label: string; value: number; delta: number }) {
  return (
    <div className="bg-white/5 rounded-lg p-2 text-center">
      <div className="text-lg font-bold">{value}</div>
      <div className="text-[10px] opacity-40">{label}</div>
      {delta !== 0 && (
        <div className={`text-[10px] flex items-center justify-center gap-0.5 mt-0.5 ${delta > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
          {delta > 0 ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
          {delta > 0 ? '+' : ''}{delta} vs 上周
        </div>
      )}
    </div>
  );
}

function DomainTrendIcon({ trend }: { trend: string }) {
  if (trend === 'up') return <TrendingUp size={14} className="text-emerald-400 shrink-0" />;
  if (trend === 'down') return <TrendingDown size={14} className="text-red-400 shrink-0" />;
  return <Minus size={14} className="text-gray-500 shrink-0" />;
}

function DeltaBadge({ value, label }: { value: number; label: string }) {
  if (value === 0) return <span className="text-xs opacity-30">持平</span>;
  const positive = value > 0;
  return (
    <span className={`text-xs ${positive ? 'text-emerald-400' : 'text-red-400'}`}>
      {positive ? '+' : ''}{value}{label}
    </span>
  );
}

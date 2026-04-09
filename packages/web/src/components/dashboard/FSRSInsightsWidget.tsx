/**
 * FSRSInsightsWidget — FSRS retention analytics with risk distribution and at-risk concepts.
 * V3.6: Forgetting risk, review efficiency, top at-risk concepts.
 */
import { useState, useEffect } from 'react';
import { ShieldAlert, ShieldCheck, Shield, RefreshCw, AlertTriangle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface RiskDist { high: number; medium: number; low: number; }
interface AtRisk {
  concept_id: string; name: string; domain: string; retrievability: number;
  stability: number; difficulty: number; reps: number; lapses: number; overdue_days: number;
}
interface InsightsData {
  total_reviewed: number;
  retention_summary: { due_count: number; overdue_count: number; avg_stability: number; avg_difficulty: number; total_reviews: number; total_lapses: number; };
  risk_distribution: RiskDist;
  efficiency: { stable_concepts: number; stable_pct: number; lapse_rate: number; avg_reps_per_concept: number; };
  at_risk_concepts: AtRisk[];
}

export function FSRSInsightsWidget() {
  const [data, setData] = useState<InsightsData | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    fetch('/api/analytics/fsrs-insights')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data || data.total_reviewed === 0) return null;

  const { retention_summary: rs, risk_distribution: rd, efficiency: eff } = data;
  const totalRisk = rd.high + rd.medium + rd.low;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <RefreshCw size={16} className="text-indigo-400" />
        <h3 className="text-sm font-semibold">间隔复习分析</h3>
        <span className="ml-auto text-xs opacity-40">{data.total_reviewed} 概念已复习</span>
      </div>

      {/* Retention summary */}
      <div className="grid grid-cols-4 gap-2 mb-3">
        <MiniStat label="待复习" value={rs.due_count} color="text-amber-400" />
        <MiniStat label="已逾期" value={rs.overdue_count} color="text-red-400" />
        <MiniStat label="平均稳定" value={rs.avg_stability.toFixed(1)} color="text-blue-400" />
        <MiniStat label="遗忘率" value={`${(eff.lapse_rate * 100).toFixed(1)}%`} color="text-orange-400" />
      </div>

      {/* Risk distribution bar */}
      {totalRisk > 0 && (
        <div className="mb-3">
          <div className="text-[10px] opacity-40 mb-1">记忆保持率分布</div>
          <div className="flex h-3 rounded-full overflow-hidden bg-white/5">
            {rd.low > 0 && <div className="bg-emerald-500/60" style={{ width: `${rd.low / totalRisk * 100}%` }} title={`低风险: ${rd.low}`} />}
            {rd.medium > 0 && <div className="bg-amber-500/60" style={{ width: `${rd.medium / totalRisk * 100}%` }} title={`中风险: ${rd.medium}`} />}
            {rd.high > 0 && <div className="bg-red-500/60" style={{ width: `${rd.high / totalRisk * 100}%` }} title={`高风险: ${rd.high}`} />}
          </div>
          <div className="flex justify-between text-[10px] mt-1">
            <span className="text-emerald-400 flex items-center gap-0.5"><ShieldCheck size={10} />{rd.low} 安全</span>
            <span className="text-amber-400 flex items-center gap-0.5"><Shield size={10} />{rd.medium} 注意</span>
            <span className="text-red-400 flex items-center gap-0.5"><ShieldAlert size={10} />{rd.high} 危险</span>
          </div>
        </div>
      )}

      {/* Efficiency stats */}
      <div className="grid grid-cols-2 gap-2 mb-3 text-center">
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-sm font-bold text-emerald-400">{eff.stable_pct}%</div>
          <div className="text-[10px] opacity-40">稳定概念</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-sm font-bold text-blue-400">{eff.avg_reps_per_concept}</div>
          <div className="text-[10px] opacity-40">平均复习次数</div>
        </div>
      </div>

      {/* At-risk concepts */}
      {data.at_risk_concepts.length > 0 && (
        <div>
          <div className="text-[10px] opacity-40 mb-1 flex items-center gap-1">
            <AlertTriangle size={10} /> 高风险概念
          </div>
          <div className="space-y-1">
            {data.at_risk_concepts.slice(0, 5).map(c => (
              <button
                key={c.concept_id}
                onClick={() => nav(`/graph?concept=${c.concept_id}`)}
                className="w-full flex items-center gap-2 p-1.5 bg-white/5 rounded-lg hover:bg-white/10 transition-colors text-left"
              >
                <div className="w-2 h-2 rounded-full shrink-0" style={{
                  backgroundColor: c.retrievability < 0.3 ? '#ef4444' : c.retrievability < 0.6 ? '#f59e0b' : '#22c55e'
                }} />
                <span className="text-xs truncate flex-1">{c.name}</span>
                <span className="text-[10px] opacity-40">{(c.retrievability * 100).toFixed(0)}%</span>
                {c.overdue_days > 0 && <span className="text-[10px] text-red-400">+{c.overdue_days}d</span>}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MiniStat({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div className="text-center">
      <div className={`text-sm font-bold ${color}`}>{value}</div>
      <div className="text-[10px] opacity-40">{label}</div>
    </div>
  );
}

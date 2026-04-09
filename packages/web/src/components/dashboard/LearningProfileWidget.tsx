/**
 * LearningProfileWidget — Unified learning profile card (replaces 5+ API calls with 1).
 * V3.7: Comprehensive overview, streak, recent activity, domains, strengths/weaknesses.
 */
import { useState, useEffect } from 'react';
import { User, Flame, TrendingUp, AlertCircle, BookOpen, RefreshCw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Domain { domain_id: string; name: string; mastered: number; total: number; progress_pct: number; }
interface BKTEntry { concept_id: string; name: string; p_mastery: number; observations: number; }
interface ProfileData {
  overview: { total_concepts: number; mastered: number; learning: number; not_started: number; completion_pct: number; avg_mastered_difficulty: number; };
  streak: { current: number; longest: number; };
  recent_7d: { events: number; mastered: number; avg_score: number; };
  domains: Domain[];
  strengths: BKTEntry[];
  weaknesses: BKTEntry[];
  review_status: { due_count: number; overdue_count: number; };
}

export function LearningProfileWidget() {
  const [data, setData] = useState<ProfileData | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    fetch('/api/analytics/learning-profile')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;
  const { overview: ov, streak, recent_7d: r7, review_status: rs } = data;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <User size={16} className="text-violet-400" />
        <h3 className="text-sm font-semibold">学习档案</h3>
        {streak.current > 0 && (
          <span className="ml-auto text-xs text-orange-400 flex items-center gap-0.5">
            <Flame size={12} />{streak.current}天
          </span>
        )}
      </div>

      {/* Overview row */}
      <div className="grid grid-cols-4 gap-2 mb-3 text-center">
        <StatCell label="已掌握" value={ov.mastered} color="text-emerald-400" />
        <StatCell label="学习中" value={ov.learning} color="text-blue-400" />
        <StatCell label="完成度" value={`${ov.completion_pct}%`} color="text-amber-400" />
        <StatCell label="平均难度" value={ov.avg_mastered_difficulty} color="text-purple-400" />
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-white/5 rounded-full mb-3 overflow-hidden">
        <div className="h-full bg-gradient-to-r from-emerald-500 to-emerald-400 rounded-full transition-all"
          style={{ width: `${Math.min(100, ov.completion_pct)}%` }} />
      </div>

      {/* Recent 7d + Review */}
      <div className="grid grid-cols-2 gap-2 mb-3">
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-[10px] opacity-40 flex items-center gap-1 mb-1"><TrendingUp size={10} />近7天</div>
          <div className="text-xs">{r7.events} 次学习 · {r7.mastered} 掌握 · 均分 {r7.avg_score}</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-[10px] opacity-40 flex items-center gap-1 mb-1"><RefreshCw size={10} />复习状态</div>
          <div className="text-xs">
            {rs.due_count > 0 ? (
              <span className={rs.overdue_count > 0 ? 'text-red-400' : 'text-amber-400'}>
                {rs.due_count} 待复习{rs.overdue_count > 0 && ` (${rs.overdue_count} 逾期)`}
              </span>
            ) : <span className="text-emerald-400">全部按时 ✓</span>}
          </div>
        </div>
      </div>

      {/* Top domains (max 4) */}
      {data.domains.length > 0 && (
        <div className="mb-3">
          <div className="text-[10px] opacity-40 mb-1">活跃领域</div>
          <div className="grid grid-cols-2 gap-1">
            {data.domains.slice(0, 4).map(d => (
              <button key={d.domain_id} onClick={() => nav(`/graph?domain=${d.domain_id}`)}
                className="flex items-center gap-1 p-1.5 bg-white/5 rounded-lg hover:bg-white/10 transition-colors text-left">
                <div className="flex-1 min-w-0">
                  <div className="text-[11px] truncate">{d.name}</div>
                  <div className="text-[10px] opacity-40">{d.mastered}/{d.total}</div>
                </div>
                <span className="text-[10px] text-emerald-400 shrink-0">{d.progress_pct}%</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Strengths/Weaknesses compact */}
      <div className="grid grid-cols-2 gap-2">
        {data.strengths.length > 0 && (
          <div>
            <div className="text-[10px] opacity-40 flex items-center gap-1 mb-1"><BookOpen size={10} />强项</div>
            {data.strengths.slice(0, 3).map(s => (
              <div key={s.concept_id} className="text-[10px] truncate text-emerald-400/70">{s.name}</div>
            ))}
          </div>
        )}
        {data.weaknesses.length > 0 && (
          <div>
            <div className="text-[10px] opacity-40 flex items-center gap-1 mb-1"><AlertCircle size={10} />待加强</div>
            {data.weaknesses.slice(0, 3).map(w => (
              <div key={w.concept_id} className="text-[10px] truncate text-amber-400/70">{w.name}</div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCell({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div>
      <div className={`text-sm font-bold ${color}`}>{value}</div>
      <div className="text-[10px] opacity-40">{label}</div>
    </div>
  );
}

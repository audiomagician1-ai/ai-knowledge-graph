/**
 * SessionReplayWidget — Learning session timeline with score progression.
 * V3.5: Shows step-by-step learning journey for recent concepts.
 */
import { useState, useEffect } from 'react';
import { Play, TrendingUp, TrendingDown, Minus, Award, RotateCcw } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Step { step: number; score: number; delta: number; mastered: boolean; timestamp: number; }
interface Session {
  concept_id: string; concept_name: string; total_attempts: number;
  first_score: number; best_score: number; latest_score: number;
  mastered: boolean; mastered_at_step: number | null; steps: Step[];
}
interface ReplayData {
  sessions: Session[]; total_events: number;
  summary: { concepts_practiced: number; total_attempts: number; mastered_count: number; best_score: number; avg_attempts_to_master: number; };
}

export function SessionReplayWidget({ limit = 8 }: { limit?: number }) {
  const [data, setData] = useState<ReplayData | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    fetch(`/api/learning/session-replay?limit=${limit}`)
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, [limit]);

  if (!data || !data.sessions.length) return null;

  const { summary } = data;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Play size={16} className="text-violet-400" />
        <h3 className="text-sm font-semibold">学习回放</h3>
        <span className="ml-auto text-xs opacity-40">
          {summary.concepts_practiced} 概念 · {summary.total_attempts} 次尝试
        </span>
      </div>

      {/* Summary bar */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-center">
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-lg font-bold text-emerald-400">{summary.mastered_count}</div>
          <div className="text-[10px] opacity-40">已掌握</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-lg font-bold text-amber-400">{summary.best_score}</div>
          <div className="text-[10px] opacity-40">最高分</div>
        </div>
        <div className="bg-white/5 rounded-lg p-2">
          <div className="text-lg font-bold text-blue-400">{summary.avg_attempts_to_master}</div>
          <div className="text-[10px] opacity-40">平均掌握次数</div>
        </div>
      </div>

      {/* Session list */}
      <div className="space-y-2">
        {data.sessions.map(s => (
          <div key={s.concept_id} className="border border-white/5 rounded-lg">
            <button
              onClick={() => setExpanded(expanded === s.concept_id ? null : s.concept_id)}
              className="w-full flex items-center gap-2 p-2 text-left hover:bg-white/5 rounded-lg transition-colors"
            >
              {s.mastered ? <Award size={14} className="text-emerald-400 shrink-0" /> : <RotateCcw size={14} className="text-amber-400 shrink-0" />}
              <span className="text-xs truncate flex-1">{s.concept_name}</span>
              <span className="text-xs opacity-50">{s.total_attempts}次</span>
              <ScoreDelta first={s.first_score} latest={s.latest_score} />
            </button>

            {expanded === s.concept_id && (
              <div className="px-3 pb-3 pt-1">
                <div className="flex gap-1 items-end h-12 mb-2">
                  {s.steps.map((st, i) => (
                    <div
                      key={i}
                      className={`flex-1 rounded-t transition-all ${st.mastered ? 'bg-emerald-500/60' : 'bg-blue-500/40'}`}
                      style={{ height: `${Math.max(4, st.score * 0.48)}px` }}
                      title={`第${st.step}次: ${st.score}分${st.delta > 0 ? ` (+${st.delta})` : ''}`}
                    />
                  ))}
                </div>
                <div className="flex justify-between text-[10px] opacity-40">
                  <span>第1次: {s.first_score}分</span>
                  <span>最佳: {s.best_score}分</span>
                  {s.mastered_at_step && <span>第{s.mastered_at_step}次掌握 ✓</span>}
                </div>
                <button
                  onClick={() => nav(`/graph?concept=${s.concept_id}`)}
                  className="mt-2 text-[10px] text-violet-400 hover:text-violet-300"
                >
                  查看概念 →
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function ScoreDelta({ first, latest }: { first: number; latest: number }) {
  const delta = latest - first;
  if (delta > 0) return <span className="text-xs text-emerald-400 flex items-center gap-0.5"><TrendingUp size={10} />+{delta}</span>;
  if (delta < 0) return <span className="text-xs text-red-400 flex items-center gap-0.5"><TrendingDown size={10} />{delta}</span>;
  return <span className="text-xs opacity-30 flex items-center gap-0.5"><Minus size={10} />0</span>;
}

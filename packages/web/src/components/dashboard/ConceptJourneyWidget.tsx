import { useState, useEffect } from 'react';
import { BookOpen, TrendingUp, Target, Clock } from 'lucide-react';

interface JourneyEvent {
  step: number;
  score: number;
  delta: number;
  mastered: boolean;
  timestamp: number;
}

interface JourneyData {
  concept_id: string;
  found: boolean;
  concept_name: string;
  domain_id: string;
  difficulty: number;
  current_status: string;
  current_score: number;
  events: JourneyEvent[];
  stats: {
    total_attempts: number;
    best_score: number;
    improvement: number;
    mastered_at_step: number | null;
    time_span_days: number;
    avg_score: number;
  };
}

export default function ConceptJourneyWidget() {
  const [data, setData] = useState<JourneyData | null>(null);
  const [conceptId, setConceptId] = useState('');
  const [searched, setSearched] = useState(false);

  const search = async () => {
    if (!conceptId.trim()) return;
    setSearched(true);
    try {
      const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const res = await fetch(`${base}/api/analytics/concept-journey/${encodeURIComponent(conceptId.trim())}`);
      if (res.ok) setData(await res.json());
    } catch { /* empty */ }
  };

  const s = data?.stats;
  const maxScore = Math.max(...(data?.events?.map(e => e.score) || [1]), 1);

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <BookOpen className="w-4 h-4 text-purple-400" />
        <h3 className="text-sm font-semibold text-white/90">概念学习旅程</h3>
      </div>

      <div className="flex gap-2 mb-3">
        <input
          value={conceptId}
          onChange={e => setConceptId(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && search()}
          placeholder="输入概念ID..."
          className="flex-1 bg-white/10 rounded-lg px-3 py-1.5 text-xs text-white/80 placeholder-white/30 outline-none"
        />
        <button onClick={search} className="px-3 py-1.5 bg-purple-500/30 text-purple-300 rounded-lg text-xs hover:bg-purple-500/50 transition">
          查询
        </button>
      </div>

      {searched && data?.found && s && (
        <>
          <div className="text-xs text-white/60 mb-2">
            <span className="text-white/90 font-medium">{data.concept_name}</span>
            <span className="ml-2">难度 {data.difficulty}</span>
            <span className={`ml-2 px-1.5 py-0.5 rounded text-[10px] ${
              data.current_status === 'mastered' ? 'bg-green-500/20 text-green-400' :
              data.current_status === 'learning' ? 'bg-blue-500/20 text-blue-400' :
              'bg-white/10 text-white/40'
            }`}>{data.current_status}</span>
          </div>

          <div className="grid grid-cols-4 gap-2 mb-3">
            {[
              { icon: Target, label: '尝试', value: s.total_attempts },
              { icon: TrendingUp, label: '最佳', value: s.best_score },
              { icon: TrendingUp, label: '提升', value: `+${s.improvement}` },
              { icon: Clock, label: '天数', value: s.time_span_days },
            ].map(({ icon: Icon, label, value }) => (
              <div key={label} className="bg-white/5 rounded-lg p-2 text-center">
                <Icon className="w-3 h-3 text-white/40 mx-auto mb-1" />
                <div className="text-xs font-bold text-white/90">{value}</div>
                <div className="text-[10px] text-white/40">{label}</div>
              </div>
            ))}
          </div>

          {/* Mini bar chart of scores */}
          <div className="flex items-end gap-0.5 h-12">
            {data.events.slice(-20).map((ev, i) => (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div
                  className={`w-full rounded-t ${ev.mastered ? 'bg-green-500/60' : 'bg-blue-500/40'}`}
                  style={{ height: `${Math.max(4, (ev.score / maxScore) * 48)}px` }}
                  title={`Step ${ev.step}: ${ev.score}分`}
                />
              </div>
            ))}
          </div>
          {data.events.length > 0 && (
            <div className="text-[10px] text-white/30 mt-1 text-center">
              最近 {Math.min(20, data.events.length)} 次评估分数
            </div>
          )}
        </>
      )}

      {searched && data && !data.found && (
        <div className="text-xs text-white/40 text-center py-4">未找到该概念的学习记录</div>
      )}

      {!searched && (
        <div className="text-xs text-white/30 text-center py-4">输入概念ID查看完整学习旅程</div>
      )}
    </div>
  );
}

/**
 * GoalRecommendWidget — Smart study goal suggestions based on learning pace.
 * V3.6: Personalized daily/weekly targets with domain focus recommendations.
 */
import { useState, useEffect } from 'react';
import { Target, Flame, BookOpen, Clock, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Recommendation {
  type: string; title: string; value: number; unit: string; rationale: string;
}
interface FocusDomain {
  domain_id: string; domain_name: string; learning_count: number;
  mastered_count: number; reason: string;
}
interface GoalData {
  recommendations: Recommendation[];
  focus_domains: FocusDomain[];
  context: {
    active_days_7d: number; avg_daily_events: number;
    avg_daily_mastered: number; current_streak: number; total_mastered: number;
  };
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  daily_concepts: <BookOpen size={14} className="text-blue-400" />,
  weekly_mastery: <Target size={14} className="text-emerald-400" />,
  daily_minutes: <Clock size={14} className="text-amber-400" />,
  streak_goal: <Flame size={14} className="text-orange-400" />,
};

export function GoalRecommendWidget() {
  const [data, setData] = useState<GoalData | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    fetch('/api/analytics/goal-recommendations')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const { context: ctx } = data;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Target size={16} className="text-emerald-400" />
        <h3 className="text-sm font-semibold">智能目标建议</h3>
        <span className="ml-auto text-xs opacity-40">
          {ctx.current_streak > 0 && <span className="text-orange-400">🔥{ctx.current_streak}天</span>}
        </span>
      </div>

      {/* Context summary */}
      <div className="grid grid-cols-3 gap-2 mb-3 text-center">
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{ctx.active_days_7d}</div>
          <div className="text-[10px] opacity-40">近7天活跃</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold">{ctx.avg_daily_events}</div>
          <div className="text-[10px] opacity-40">日均学习</div>
        </div>
        <div className="bg-white/5 rounded-lg p-1.5">
          <div className="text-sm font-bold text-emerald-400">{ctx.total_mastered}</div>
          <div className="text-[10px] opacity-40">已掌握</div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="space-y-2 mb-3">
        {data.recommendations.map((rec, i) => (
          <div key={i} className="flex items-start gap-2 p-2 bg-white/5 rounded-lg">
            <div className="mt-0.5 shrink-0">{TYPE_ICONS[rec.type] || <Target size={14} />}</div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium">{rec.title}</div>
              <div className="text-[10px] opacity-40 mt-0.5">{rec.rationale}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Focus domains */}
      {data.focus_domains.length > 0 && (
        <div>
          <div className="text-[10px] opacity-40 mb-1">推荐专注领域</div>
          <div className="space-y-1">
            {data.focus_domains.map(d => (
              <button
                key={d.domain_id}
                onClick={() => nav(`/graph?domain=${d.domain_id}`)}
                className="w-full flex items-center gap-2 p-1.5 hover:bg-white/10 rounded-lg transition-colors text-left"
              >
                <span className="text-xs truncate flex-1">{d.domain_name}</span>
                <span className="text-[10px] opacity-40">{d.learning_count} 进行中</span>
                <ArrowRight size={10} className="opacity-30 shrink-0" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

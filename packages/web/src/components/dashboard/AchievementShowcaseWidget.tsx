/**
 * AchievementShowcaseWidget — Display earned achievements with tier badges.
 * V4.5: Shows unlocked achievements grouped by category with progress stats.
 */
import { useState, useEffect } from 'react';
import { Trophy, Lock, Star, Flame, BookOpen, Target, Zap } from 'lucide-react';

interface Achievement {
  key: string; category: string; name: string; description: string;
  tier: string; unlocked: boolean; unlocked_at?: string;
}
interface AchievementData {
  total: number; unlocked_count: number;
  categories: Record<string, { total: number; unlocked: number }>;
  achievements: Achievement[];
}

const TIER_COLORS: Record<string, string> = {
  bronze: 'text-orange-400 bg-orange-500/20',
  silver: 'text-slate-300 bg-slate-400/20',
  gold: 'text-yellow-400 bg-yellow-500/20',
  platinum: 'text-cyan-300 bg-cyan-400/20',
};
const CAT_ICONS: Record<string, React.ReactNode> = {
  learning: <BookOpen size={10} />, streak: <Flame size={10} />,
  domain: <Target size={10} />, assessment: <Star size={10} />,
  review: <Zap size={10} />, special: <Trophy size={10} />,
};

export function AchievementShowcaseWidget() {
  const [data, setData] = useState<AchievementData | null>(null);

  useEffect(() => {
    fetch('/api/learning/achievements')
      .then(r => r.ok ? r.json() : null)
      .then(d => d && setData(d))
      .catch(() => {});
  }, []);

  if (!data) return null;

  const unlocked = data.achievements.filter(a => a.unlocked);
  const locked = data.achievements.filter(a => !a.unlocked);
  const pct = data.total > 0 ? Math.round((data.unlocked_count / data.total) * 100) : 0;

  return (
    <div className="rounded-xl border border-white/10 bg-white/5 p-4">
      <div className="flex items-center gap-2 mb-3">
        <Trophy size={16} className="text-yellow-400" />
        <h3 className="text-sm font-semibold">成就展示</h3>
        <span className="ml-auto text-xs opacity-40">{data.unlocked_count}/{data.total} ({pct}%)</span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-white/10 rounded-full h-1.5 mb-3">
        <div className="h-full rounded-full bg-yellow-400 transition-all" style={{ width: `${pct}%` }} />
      </div>

      {/* Category breakdown */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        {Object.entries(data.categories).map(([cat, info]) => (
          <span key={cat} className="inline-flex items-center gap-1 px-2 py-0.5 bg-white/5 rounded-full text-[10px]">
            {CAT_ICONS[cat] || <Star size={10} />}
            <span className="opacity-60">{cat}</span>
            <span className={info.unlocked > 0 ? 'text-yellow-400' : 'opacity-30'}>{info.unlocked}/{info.total}</span>
          </span>
        ))}
      </div>

      {/* Unlocked achievements */}
      {unlocked.length > 0 && (
        <div className="space-y-1.5 mb-3">
          {unlocked.slice(0, 5).map(a => (
            <div key={a.key} className="flex items-center gap-2 p-1.5 bg-white/5 rounded-lg">
              <div className={`p-1 rounded ${TIER_COLORS[a.tier] || TIER_COLORS.bronze}`}>
                <Trophy size={12} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-xs font-medium truncate">{a.name}</div>
                <div className="text-[10px] opacity-40 truncate">{a.description}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Next to unlock */}
      {locked.length > 0 && (
        <div>
          <div className="text-[10px] opacity-30 mb-1">即将解锁</div>
          <div className="flex items-center gap-2 p-1.5 bg-white/5 rounded-lg opacity-50">
            <Lock size={12} className="shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-xs truncate">{locked[0].name}</div>
              <div className="text-[10px] opacity-40 truncate">{locked[0].description}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

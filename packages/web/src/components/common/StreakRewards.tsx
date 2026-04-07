import { useMemo } from 'react';
import { Flame, Trophy, Star, Zap, Crown, Heart } from 'lucide-react';

/**
 * StreakRewards — Display streak milestone rewards.
 *
 * Milestones: 3, 7, 14, 30, 60, 100, 365 days.
 * Each milestone unlocks a visual badge with unique icon + color.
 */

interface StreakMilestone {
  days: number;
  label: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  description: string;
}

const MILESTONES: StreakMilestone[] = [
  { days: 3, label: '起步者', icon: <Flame size={16} />, color: '#f97316', bgColor: '#f9731620', description: '连续学习3天' },
  { days: 7, label: '坚持者', icon: <Star size={16} />, color: '#eab308', bgColor: '#eab30820', description: '一周不间断' },
  { days: 14, label: '学霸', icon: <Zap size={16} />, color: '#3b82f6', bgColor: '#3b82f620', description: '两周连续' },
  { days: 30, label: '大师', icon: <Trophy size={16} />, color: '#22c55e', bgColor: '#22c55e20', description: '月度冠军' },
  { days: 60, label: '传说', icon: <Crown size={16} />, color: '#8b5cf6', bgColor: '#8b5cf620', description: '两月坚持' },
  { days: 100, label: '百日王', icon: <Crown size={16} />, color: '#ec4899', bgColor: '#ec489920', description: '百日学习' },
  { days: 365, label: '年度传奇', icon: <Heart size={16} />, color: '#ef4444', bgColor: '#ef444420', description: '整年无休' },
];

interface StreakRewardsProps {
  currentStreak: number;
  longestStreak: number;
  compact?: boolean;
}

export function StreakRewards({ currentStreak, longestStreak, compact = false }: StreakRewardsProps) {
  const effectiveStreak = Math.max(currentStreak, longestStreak);

  const unlockedMilestones = useMemo(
    () => MILESTONES.filter((m) => effectiveStreak >= m.days),
    [effectiveStreak]
  );

  const nextMilestone = useMemo(
    () => MILESTONES.find((m) => effectiveStreak < m.days),
    [effectiveStreak]
  );

  if (compact) {
    // Show only badges in a row
    return (
      <div className="flex items-center gap-1.5 flex-wrap">
        {MILESTONES.map((m) => {
          const unlocked = effectiveStreak >= m.days;
          return (
            <div
              key={m.days}
              className="flex items-center gap-1 px-2 py-1 rounded-full text-xs transition-all"
              style={{
                backgroundColor: unlocked ? m.bgColor : 'var(--color-surface-2)',
                color: unlocked ? m.color : 'var(--color-text-secondary)',
                opacity: unlocked ? 1 : 0.4,
              }}
              title={`${m.label}: ${m.description}`}
            >
              {m.icon}
              <span className="font-medium">{m.days}</span>
            </div>
          );
        })}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Unlocked badges */}
      {unlockedMilestones.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {unlockedMilestones.map((m) => (
            <div
              key={m.days}
              className="flex items-center gap-2 px-3 py-2 rounded-lg"
              style={{ backgroundColor: m.bgColor, color: m.color }}
            >
              {m.icon}
              <div>
                <p className="text-xs font-bold">{m.label}</p>
                <p className="text-[10px] opacity-70">{m.description}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Next milestone progress */}
      {nextMilestone && (
        <div className="rounded-lg p-3" style={{ backgroundColor: 'var(--color-surface-0)' }}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs opacity-60">下一个里程碑</span>
            <span className="text-xs font-medium" style={{ color: nextMilestone.color }}>
              {nextMilestone.label} ({nextMilestone.days}天)
            </span>
          </div>
          <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-2)' }}>
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${Math.min(100, (effectiveStreak / nextMilestone.days) * 100)}%`,
                backgroundColor: nextMilestone.color,
              }}
            />
          </div>
          <p className="text-xs opacity-40 mt-1 text-right">
            {effectiveStreak} / {nextMilestone.days} 天 ({Math.round((effectiveStreak / nextMilestone.days) * 100)}%)
          </p>
        </div>
      )}
    </div>
  );
}

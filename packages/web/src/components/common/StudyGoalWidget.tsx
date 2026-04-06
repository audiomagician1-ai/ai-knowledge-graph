import { useState } from 'react';
import { useStudyGoal } from '@/lib/hooks/useStudyGoal';
import { Target, CheckCircle2, Settings, X, TrendingUp } from 'lucide-react';

/**
 * Study Goal Widget — shows daily goal progress with ring visualization.
 * Place in DashboardPage or HomePage.
 */
export function StudyGoalWidget() {
  const {
    goal,
    updateGoal,
    todayRecord,
    conceptProgress,
    timeProgress,
    isConceptGoalMet,
    isTimeGoalMet,
    isFullGoalMet,
    weekHistory,
    goalStreak,
  } = useStudyGoal();

  const [showSettings, setShowSettings] = useState(false);

  if (!goal.enabled) return null;

  const overallProgress = Math.round((conceptProgress + timeProgress) / 2);

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Target size={18} style={{ color: 'var(--color-accent)' }} />
          今日目标
          {isFullGoalMet && (
            <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: '#22c55e20', color: '#22c55e' }}>
              ✨ 已达成
            </span>
          )}
        </h2>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-1.5 rounded-md hover:bg-white/10 transition-colors"
          aria-label="设置学习目标"
        >
          {showSettings ? <X size={16} /> : <Settings size={16} />}
        </button>
      </div>

      {showSettings ? (
        <GoalSettings goal={goal} onUpdate={updateGoal} onClose={() => setShowSettings(false)} />
      ) : (
        <>
          {/* Progress rings */}
          <div className="flex items-center justify-center gap-8 mb-4">
            <ProgressRing
              progress={conceptProgress}
              color="#3b82f6"
              label="概念"
              value={`${todayRecord.concepts}/${goal.dailyConceptTarget}`}
              done={isConceptGoalMet}
            />
            <ProgressRing
              progress={timeProgress}
              color="#8b5cf6"
              label="时间"
              value={`${todayRecord.minutes}/${goal.dailyTimeTarget}min`}
              done={isTimeGoalMet}
            />
          </div>

          {/* Goal streak */}
          {goalStreak > 0 && (
            <div className="text-center text-sm mb-3" style={{ color: 'var(--color-text-secondary)' }}>
              <TrendingUp size={14} className="inline mr-1" style={{ color: '#f59e0b' }} />
              连续 {goalStreak} 天达标
            </div>
          )}

          {/* Mini week chart */}
          <div className="flex items-end gap-1.5 h-10 px-2">
            {weekHistory.map((day) => {
              const dayGoalMet =
                day.concepts >= goal.dailyConceptTarget &&
                day.minutes >= goal.dailyTimeTarget;
              const pct = goal.dailyConceptTarget > 0
                ? Math.min(100, Math.round((day.concepts / goal.dailyConceptTarget) * 100))
                : 0;
              return (
                <div
                  key={day.date}
                  className="flex-1 rounded-t transition-all"
                  title={`${day.date}: ${day.concepts} 概念, ${day.minutes} 分钟`}
                  style={{
                    height: `${Math.max(4, pct)}%`,
                    backgroundColor: dayGoalMet ? '#22c55e' : pct > 0 ? '#3b82f680' : 'var(--color-surface-3)',
                  }}
                />
              );
            })}
          </div>
          <div className="flex justify-between px-2 mt-1">
            <span className="text-[10px] opacity-40">7天前</span>
            <span className="text-[10px] opacity-40">今天</span>
          </div>
        </>
      )}
    </section>
  );
}

/** SVG ring progress indicator */
function ProgressRing({
  progress,
  color,
  label,
  value,
  done,
}: {
  progress: number;
  color: string;
  label: string;
  value: string;
  done: boolean;
}) {
  const radius = 36;
  const stroke = 5;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - progress / 100);

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: 80, height: 80 }}>
        <svg width="80" height="80" viewBox="0 0 80 80">
          {/* Background ring */}
          <circle
            cx="40"
            cy="40"
            r={radius}
            fill="none"
            stroke="var(--color-surface-3)"
            strokeWidth={stroke}
          />
          {/* Progress ring */}
          <circle
            cx="40"
            cy="40"
            r={radius}
            fill="none"
            stroke={done ? '#22c55e' : color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            transform="rotate(-90 40 40)"
            style={{ transition: 'stroke-dashoffset 0.5s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          {done ? (
            <CheckCircle2 size={20} style={{ color: '#22c55e' }} />
          ) : (
            <span className="text-sm font-bold">{progress}%</span>
          )}
        </div>
      </div>
      <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
        {label} {value}
      </span>
    </div>
  );
}

/** Goal settings editor */
function GoalSettings({
  goal,
  onUpdate,
  onClose,
}: {
  goal: { dailyConceptTarget: number; dailyTimeTarget: number; enabled: boolean };
  onUpdate: (patch: Partial<typeof goal>) => void;
  onClose: () => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium block mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
          每日概念目标
        </label>
        <div className="flex items-center gap-3">
          {[1, 3, 5, 10].map((v) => (
            <button
              key={v}
              onClick={() => onUpdate({ dailyConceptTarget: v })}
              className="px-3 py-1.5 rounded-lg text-sm transition-colors"
              style={{
                backgroundColor: goal.dailyConceptTarget === v ? 'var(--color-accent-primary)' : 'var(--color-surface-3)',
                color: goal.dailyConceptTarget === v ? '#fff' : 'var(--color-text-primary)',
              }}
            >
              {v} 个
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="text-sm font-medium block mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>
          每日时间目标
        </label>
        <div className="flex items-center gap-3">
          {[5, 15, 30, 60].map((v) => (
            <button
              key={v}
              onClick={() => onUpdate({ dailyTimeTarget: v })}
              className="px-3 py-1.5 rounded-lg text-sm transition-colors"
              style={{
                backgroundColor: goal.dailyTimeTarget === v ? 'var(--color-accent-primary)' : 'var(--color-surface-3)',
                color: goal.dailyTimeTarget === v ? '#fff' : 'var(--color-text-primary)',
              }}
            >
              {v} 分钟
            </button>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between">
        <label className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
          启用每日目标
        </label>
        <button
          onClick={() => onUpdate({ enabled: !goal.enabled })}
          className="w-10 h-6 rounded-full relative transition-colors"
          style={{ backgroundColor: goal.enabled ? 'var(--color-accent-primary)' : 'var(--color-surface-3)' }}
          aria-label="切换每日目标"
        >
          <div
            className="w-4 h-4 rounded-full bg-white absolute top-1 transition-all"
            style={{ left: goal.enabled ? '22px' : '4px' }}
          />
        </button>
      </div>

      <button
        onClick={onClose}
        className="w-full py-2 rounded-lg text-sm transition-colors"
        style={{ backgroundColor: 'var(--color-surface-3)' }}
      >
        完成设置
      </button>
    </div>
  );
}

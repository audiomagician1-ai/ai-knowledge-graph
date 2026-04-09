import { useState } from 'react';
import { useStudyGoal } from '@/lib/hooks/useStudyGoal';
import { Target, Settings, X, TrendingUp } from 'lucide-react';
import { ProgressRing, GoalSettings } from './StudyGoalParts';

/**
 * Study Goal Widget — shows daily goal progress with ring visualization.
 * Place in DashboardPage or HomePage.
 */
export function StudyGoalWidget() {
  const {
    goal, updateGoal, todayRecord, conceptProgress, timeProgress,
    isConceptGoalMet, isTimeGoalMet, isFullGoalMet, weekHistory, goalStreak,
  } = useStudyGoal();

  const [showSettings, setShowSettings] = useState(false);

  if (!goal.enabled) return null;

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
          <div className="flex items-center justify-center gap-8 mb-4">
            <ProgressRing progress={conceptProgress} color="#3b82f6" label="概念"
              value={`${todayRecord.concepts}/${goal.dailyConceptTarget}`} done={isConceptGoalMet} />
            <ProgressRing progress={timeProgress} color="#8b5cf6" label="时间"
              value={`${todayRecord.minutes}/${goal.dailyTimeTarget}min`} done={isTimeGoalMet} />
          </div>

          {goalStreak > 0 && (
            <div className="text-center text-sm mb-3" style={{ color: 'var(--color-text-secondary)' }}>
              <TrendingUp size={14} className="inline mr-1" style={{ color: '#f59e0b' }} />
              连续 {goalStreak} 天达标
            </div>
          )}

          <div className="flex items-end gap-1.5 h-10 px-2">
            {weekHistory.map((day) => {
              const dayGoalMet = day.concepts >= goal.dailyConceptTarget && day.minutes >= goal.dailyTimeTarget;
              const pct = goal.dailyConceptTarget > 0 ? Math.min(100, Math.round((day.concepts / goal.dailyConceptTarget) * 100)) : 0;
              return (
                <div key={day.date} className="flex-1 rounded-t transition-all"
                  title={`${day.date}: ${day.concepts} 概念, ${day.minutes} 分钟`}
                  style={{ height: `${Math.max(4, pct)}%`, backgroundColor: dayGoalMet ? '#22c55e' : pct > 0 ? '#3b82f680' : 'var(--color-surface-3)' }} />
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

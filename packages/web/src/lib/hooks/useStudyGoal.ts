import { useCallback, useMemo } from 'react';
import { useLocalStorage } from './useLocalStorage';

export interface StudyGoal {
  /** Daily concept goal (number of concepts to learn/review per day) */
  dailyConceptTarget: number;
  /** Daily time goal in minutes */
  dailyTimeTarget: number;
  /** Whether goal system is enabled */
  enabled: boolean;
}

interface DailyRecord {
  /** YYYY-MM-DD */
  date: string;
  /** Number of concepts interacted with */
  concepts: number;
  /** Minutes spent */
  minutes: number;
}

const DEFAULT_GOAL: StudyGoal = {
  dailyConceptTarget: 3,
  dailyTimeTarget: 15,
  enabled: true,
};

const todayKey = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
};

/**
 * Study goal tracking hook.
 * Persists goal settings + daily progress in localStorage.
 */
export function useStudyGoal() {
  const [goal, setGoal] = useLocalStorage<StudyGoal>('akg-study-goal', DEFAULT_GOAL);
  const [dailyLog, setDailyLog] = useLocalStorage<Record<string, DailyRecord>>(
    'akg-study-daily-log',
    {}
  );

  const today = todayKey();
  const todayRecord: DailyRecord = useMemo(
    () => dailyLog[today] || { date: today, concepts: 0, minutes: 0 },
    [dailyLog, today]
  );

  /** Record a concept interaction for today */
  const recordConceptToday = useCallback(() => {
    setDailyLog((prev) => {
      const existing = prev[today] || { date: today, concepts: 0, minutes: 0 };
      return {
        ...prev,
        [today]: { ...existing, concepts: existing.concepts + 1 },
      };
    });
  }, [today, setDailyLog]);

  /** Update today's learning time (in minutes) */
  const recordTimeToday = useCallback(
    (minutes: number) => {
      setDailyLog((prev) => {
        const existing = prev[today] || { date: today, concepts: 0, minutes: 0 };
        return {
          ...prev,
          [today]: { ...existing, minutes },
        };
      });
    },
    [today, setDailyLog]
  );

  /** Update goal settings */
  const updateGoal = useCallback(
    (patch: Partial<StudyGoal>) => {
      setGoal((prev) => ({ ...prev, ...patch }));
    },
    [setGoal]
  );

  /** Progress percentage (0-100, capped at 100) */
  const conceptProgress = goal.dailyConceptTarget > 0
    ? Math.min(100, Math.round((todayRecord.concepts / goal.dailyConceptTarget) * 100))
    : 100;

  const timeProgress = goal.dailyTimeTarget > 0
    ? Math.min(100, Math.round((todayRecord.minutes / goal.dailyTimeTarget) * 100))
    : 100;

  const isConceptGoalMet = todayRecord.concepts >= goal.dailyConceptTarget;
  const isTimeGoalMet = todayRecord.minutes >= goal.dailyTimeTarget;
  const isFullGoalMet = isConceptGoalMet && isTimeGoalMet;

  /** Last 7 days of records for trend display */
  const weekHistory = useMemo(() => {
    const result: DailyRecord[] = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86_400_000);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      result.push(dailyLog[key] || { date: key, concepts: 0, minutes: 0 });
    }
    return result;
  }, [dailyLog]);

  /** Consecutive days goal was fully met */
  const goalStreak = useMemo(() => {
    let streak = 0;
    for (let i = 0; ; i++) {
      const d = new Date(Date.now() - i * 86_400_000);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      const rec = dailyLog[key];
      if (!rec) break;
      if (
        rec.concepts >= goal.dailyConceptTarget &&
        rec.minutes >= goal.dailyTimeTarget
      ) {
        streak++;
      } else if (i > 0) {
        // Today might not be complete yet, so skip day 0 check
        break;
      }
    }
    return streak;
  }, [dailyLog, goal]);

  return {
    goal,
    updateGoal,
    todayRecord,
    recordConceptToday,
    recordTimeToday,
    conceptProgress,
    timeProgress,
    isConceptGoalMet,
    isTimeGoalMet,
    isFullGoalMet,
    weekHistory,
    goalStreak,
  };
}

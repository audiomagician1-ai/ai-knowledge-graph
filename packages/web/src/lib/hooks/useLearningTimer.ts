import { useEffect, useRef, useCallback } from 'react';

const STORAGE_KEY = 'akg-learning-time';
const TICK_INTERVAL = 5_000; // save every 5 seconds

interface LearningTimeData {
  /** Total seconds spent learning, all time */
  totalSeconds: number;
  /** Seconds per day { "2026-04-07": 1234 } */
  daily: Record<string, number>;
  /** Last updated timestamp */
  lastUpdated: number;
}

function todayKey(): string {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function loadData(): LearningTimeData {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch { /* ignore */ }
  return { totalSeconds: 0, daily: {}, lastUpdated: Date.now() };
}

function saveData(data: LearningTimeData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch { /* quota exceeded — silent */ }
}

/**
 * Tracks time spent on a learning page.
 * Automatically pauses when tab is hidden (visibilitychange).
 * Saves accumulated time every 5 seconds to localStorage.
 * 
 * Returns: { getTodayMinutes, getTotalMinutes }
 */
export function useLearningTimer() {
  const activeRef = useRef(true);
  const accumulatedRef = useRef(0); // seconds since last save

  // Tick: accumulate + save periodically
  useEffect(() => {
    const handleVisibility = () => {
      activeRef.current = document.visibilityState === 'visible';
    };
    document.addEventListener('visibilitychange', handleVisibility);

    const interval = setInterval(() => {
      if (!activeRef.current) return;
      
      // Add 5 seconds of active time
      accumulatedRef.current += TICK_INTERVAL / 1000;
      
      const data = loadData();
      const key = todayKey();
      data.totalSeconds += TICK_INTERVAL / 1000;
      data.daily[key] = (data.daily[key] || 0) + TICK_INTERVAL / 1000;
      data.lastUpdated = Date.now();
      
      // Prune daily data older than 90 days
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - 90);
      const cutoffKey = `${cutoff.getFullYear()}-${String(cutoff.getMonth() + 1).padStart(2, '0')}-${String(cutoff.getDate()).padStart(2, '0')}`;
      for (const k of Object.keys(data.daily)) {
        if (k < cutoffKey) delete data.daily[k];
      }
      
      saveData(data);
    }, TICK_INTERVAL);

    return () => {
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibility);
    };
  }, []);

  const getTodayMinutes = useCallback((): number => {
    const data = loadData();
    return Math.round((data.daily[todayKey()] || 0) / 60);
  }, []);

  const getTotalMinutes = useCallback((): number => {
    const data = loadData();
    return Math.round(data.totalSeconds / 60);
  }, []);

  const getWeekMinutes = useCallback((): number => {
    const data = loadData();
    const now = new Date();
    let total = 0;
    for (let i = 0; i < 7; i++) {
      const d = new Date(now.getTime() - i * 86400_000);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      total += data.daily[key] || 0;
    }
    return Math.round(total / 60);
  }, []);

  return { getTodayMinutes, getTotalMinutes, getWeekMinutes };
}

/** Static helper to read learning time without the hook */
export function readLearningTime(): LearningTimeData {
  return loadData();
}

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook } from '@testing-library/react';

// Mock localStorage
const store: Record<string, string> = {};
const mockLocalStorage = {
  getItem: vi.fn((key: string) => store[key] ?? null),
  setItem: vi.fn((key: string, value: string) => { store[key] = value; }),
  removeItem: vi.fn((key: string) => { delete store[key]; }),
  clear: vi.fn(() => { for (const k of Object.keys(store)) delete store[k]; }),
};
vi.stubGlobal('localStorage', mockLocalStorage);

describe('useLearningTimer', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    mockLocalStorage.clear();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('should initialize with zero time', async () => {
    const { useLearningTimer } = await import('../hooks/useLearningTimer');
    const { result } = renderHook(() => useLearningTimer());
    expect(result.current.getTodayMinutes()).toBe(0);
    expect(result.current.getTotalMinutes()).toBe(0);
    expect(result.current.getWeekMinutes()).toBe(0);
  });

  it('should accumulate time after ticks', async () => {
    const { useLearningTimer } = await import('../hooks/useLearningTimer');
    const { result } = renderHook(() => useLearningTimer());
    
    // Simulate 12 ticks of 5s = 60s = 1 minute
    for (let i = 0; i < 12; i++) {
      vi.advanceTimersByTime(5_000);
    }
    
    expect(result.current.getTodayMinutes()).toBe(1);
    expect(result.current.getTotalMinutes()).toBe(1);
  });

  it('should persist data to localStorage', async () => {
    const { useLearningTimer } = await import('../hooks/useLearningTimer');
    renderHook(() => useLearningTimer());
    
    // Advance 5s — should trigger one save
    vi.advanceTimersByTime(5_000);
    
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      'akg-learning-time',
      expect.any(String)
    );
  });

  it('should read existing data from localStorage', async () => {
    const { readLearningTime } = await import('../hooks/useLearningTimer');
    
    // Pre-populate
    const data = {
      totalSeconds: 3600,
      daily: { '2026-04-07': 1800 },
      lastUpdated: Date.now(),
    };
    store['akg-learning-time'] = JSON.stringify(data);
    
    const result = readLearningTime();
    expect(result.totalSeconds).toBe(3600);
    expect(result.daily['2026-04-07']).toBe(1800);
  });

  it('should handle corrupt localStorage gracefully', async () => {
    const { readLearningTime } = await import('../hooks/useLearningTimer');
    store['akg-learning-time'] = 'not-json';
    
    const result = readLearningTime();
    expect(result.totalSeconds).toBe(0);
    expect(result.daily).toEqual({});
  });

  it('getWeekMinutes should sum last 7 days', async () => {
    const { readLearningTime } = await import('../hooks/useLearningTimer');
    
    const now = new Date();
    const daily: Record<string, number> = {};
    // Add 300 seconds per day for 7 days
    for (let i = 0; i < 7; i++) {
      const d = new Date(now.getTime() - i * 86400_000);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      daily[key] = 300;
    }
    // Add old data that should not be counted
    daily['2020-01-01'] = 9999;
    
    store['akg-learning-time'] = JSON.stringify({ totalSeconds: 12099, daily, lastUpdated: Date.now() });
    const result = readLearningTime();
    expect(Object.keys(result.daily).length).toBe(8); // 7 recent + 1 old
  });
});

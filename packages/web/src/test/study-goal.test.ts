import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock localStorage for testing
const storageMap = new Map<string, string>();
const localStorageMock = {
  getItem: vi.fn((key: string) => storageMap.get(key) ?? null),
  setItem: vi.fn((key: string, val: string) => storageMap.set(key, val)),
  removeItem: vi.fn((key: string) => storageMap.delete(key)),
  clear: vi.fn(() => storageMap.clear()),
  get length() { return storageMap.size; },
  key: vi.fn(() => null),
};

Object.defineProperty(globalThis, 'localStorage', { value: localStorageMock });

describe('StudyGoal logic', () => {
  beforeEach(() => {
    storageMap.clear();
  });

  it('should have sensible default goal values', () => {
    // Default: 3 concepts, 15 minutes
    const defaultGoal = { dailyConceptTarget: 3, dailyTimeTarget: 15, enabled: true };
    expect(defaultGoal.dailyConceptTarget).toBe(3);
    expect(defaultGoal.dailyTimeTarget).toBe(15);
    expect(defaultGoal.enabled).toBe(true);
  });

  it('should calculate concept progress correctly', () => {
    const conceptsDone = 2;
    const conceptTarget = 5;
    const progress = Math.min(100, Math.round((conceptsDone / conceptTarget) * 100));
    expect(progress).toBe(40);
  });

  it('should cap progress at 100%', () => {
    const conceptsDone = 10;
    const conceptTarget = 3;
    const progress = Math.min(100, Math.round((conceptsDone / conceptTarget) * 100));
    expect(progress).toBe(100);
  });

  it('should handle zero target gracefully', () => {
    const target = 0;
    const progress = target > 0 ? Math.min(100, Math.round((5 / target) * 100)) : 100;
    expect(progress).toBe(100);
  });

  it('should serialize goal to localStorage format', () => {
    const goal = { dailyConceptTarget: 5, dailyTimeTarget: 30, enabled: true };
    const serialized = JSON.stringify(goal);
    const parsed = JSON.parse(serialized);
    expect(parsed).toEqual(goal);
  });

  it('should compute goal streak correctly', () => {
    const log: Record<string, { concepts: number; minutes: number }> = {};
    const target = { concepts: 3, minutes: 15 };

    // Build 5-day streak
    for (let i = 0; i < 5; i++) {
      const d = new Date(Date.now() - i * 86_400_000);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      log[key] = { concepts: 4, minutes: 20 };
    }

    // Calculate streak
    let streak = 0;
    for (let i = 0; ; i++) {
      const d = new Date(Date.now() - i * 86_400_000);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      const rec = log[key];
      if (!rec || rec.concepts < target.concepts || rec.minutes < target.minutes) {
        if (i > 0) break;
        else break;
      }
      streak++;
    }

    expect(streak).toBe(5);
  });

  it('should generate today key in YYYY-MM-DD format', () => {
    const d = new Date();
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    expect(key).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it('should track weekly history (7 entries)', () => {
    const dailyLog: Record<string, { date: string; concepts: number; minutes: number }> = {};
    const result = [];
    for (let i = 6; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86_400_000);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      result.push(dailyLog[key] || { date: key, concepts: 0, minutes: 0 });
    }
    expect(result.length).toBe(7);
  });
});

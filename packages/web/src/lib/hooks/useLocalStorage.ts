import { useState, useCallback } from 'react';

/**
 * Hook for persisted state in localStorage with type safety.
 * 
 * Features:
 * - Type-safe with generics
 * - Lazy initialization (reads localStorage only on first render)
 * - Graceful fallback on parse errors or quota exceeded
 * - Returns setter similar to useState
 * 
 * Usage:
 *   const [theme, setTheme] = useLocalStorage('theme', 'dark');
 *   setTheme('light'); // persists immediately
 */
export function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T | ((prev: T) => T)) => void] {
  // Lazy initialization: only read from localStorage once
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item !== null ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    setStoredValue((prev) => {
      const nextValue = value instanceof Function ? value(prev) : value;
      try {
        localStorage.setItem(key, JSON.stringify(nextValue));
      } catch {
        // Quota exceeded or unavailable — value still updates in memory
      }
      return nextValue;
    });
  }, [key]);

  return [storedValue, setValue];
}

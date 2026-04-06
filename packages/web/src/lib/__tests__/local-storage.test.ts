import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useLocalStorage } from '../hooks/useLocalStorage';

vi.stubGlobal('localStorage', {
  _store: {} as Record<string, string>,
  getItem(key: string) { return this._store[key] ?? null; },
  setItem(key: string, value: string) { this._store[key] = value; },
  removeItem(key: string) { delete this._store[key]; },
  clear() { this._store = {}; },
});

beforeEach(() => {
  localStorage.clear();
});

describe('useLocalStorage', () => {
  it('should return initial value when key does not exist', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'default'));
    expect(result.current[0]).toBe('default');
  });

  it('should persist value to localStorage', () => {
    const { result } = renderHook(() => useLocalStorage('theme', 'dark'));
    act(() => result.current[1]('light'));
    expect(result.current[0]).toBe('light');
    expect(JSON.parse(localStorage.getItem('theme')!)).toBe('light');
  });

  it('should read existing value from localStorage', () => {
    localStorage.setItem('count', JSON.stringify(42));
    const { result } = renderHook(() => useLocalStorage('count', 0));
    expect(result.current[0]).toBe(42);
  });

  it('should handle function updater', () => {
    const { result } = renderHook(() => useLocalStorage('counter', 0));
    act(() => result.current[1]((prev) => prev + 1));
    expect(result.current[0]).toBe(1);
    act(() => result.current[1]((prev) => prev + 5));
    expect(result.current[0]).toBe(6);
  });

  it('should fallback to initial on invalid JSON', () => {
    localStorage.setItem('bad', 'not-json');
    const { result } = renderHook(() => useLocalStorage('bad', 'fallback'));
    expect(result.current[0]).toBe('fallback');
  });

  it('should handle object values', () => {
    const { result } = renderHook(() => useLocalStorage('user', { name: 'test' }));
    act(() => result.current[1]({ name: 'updated' }));
    expect(result.current[0]).toEqual({ name: 'updated' });
    expect(JSON.parse(localStorage.getItem('user')!)).toEqual({ name: 'updated' });
  });

  it('should handle array values', () => {
    const { result } = renderHook(() => useLocalStorage<string[]>('items', []));
    act(() => result.current[1](['a', 'b']));
    expect(result.current[0]).toEqual(['a', 'b']);
  });

  it('should handle boolean values', () => {
    const { result } = renderHook(() => useLocalStorage('flag', false));
    act(() => result.current[1](true));
    expect(result.current[0]).toBe(true);
  });
});

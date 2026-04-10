/**
 * useFetchWidget — Reusable fetch hook with AbortController cleanup for dashboard widgets.
 * V4.7: Addresses #65 — prevents setState on unmounted components.
 *
 * Usage:
 *   const { data, loading, error } = useFetchWidget<MyType>('/api/analytics/my-endpoint');
 */
import { useState, useEffect, useRef } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || '';

interface FetchWidgetResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useFetchWidget<T = unknown>(path: string, deps: unknown[] = []): FetchWidgetResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    const controller = new AbortController();
    setLoading(true);
    setError(null);

    fetch(`${API_BASE}${path}`, { signal: controller.signal })
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(json => {
        if (mountedRef.current) {
          setData(json as T);
          setLoading(false);
        }
      })
      .catch(err => {
        if (mountedRef.current && err.name !== 'AbortError') {
          setError(err.message);
          setLoading(false);
        }
      });

    return () => {
      mountedRef.current = false;
      controller.abort();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { data, loading, error };
}

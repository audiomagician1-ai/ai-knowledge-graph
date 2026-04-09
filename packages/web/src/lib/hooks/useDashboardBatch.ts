/**
 * useDashboardBatch — V2.4 performance: fetches weekly-report + study-patterns + learning-velocity
 * in a single API call instead of 3 separate requests.
 *
 * Uses a module-level cache so multiple lazy-loaded widgets share the same data
 * without re-fetching (cache valid for 60 seconds).
 */

import { useState, useEffect } from 'react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

interface BatchData {
  weekly_report: Record<string, unknown> | null;
  study_patterns: Record<string, unknown> | null;
  learning_velocity: Record<string, unknown> | null;
}

// Module-level cache (shared across all widget instances)
let cachedData: BatchData | null = null;
let cacheTimestamp = 0;
let pendingFetch: Promise<BatchData | null> | null = null;
const CACHE_TTL_MS = 60_000; // 60 seconds

async function fetchBatch(): Promise<BatchData | null> {
  // Return cached data if fresh
  if (cachedData && Date.now() - cacheTimestamp < CACHE_TTL_MS) {
    return cachedData;
  }

  // Deduplicate concurrent requests
  if (pendingFetch) return pendingFetch;

  pendingFetch = (async () => {
    try {
      const res = await fetchWithRetry(`${API_BASE}/analytics/dashboard-batch`, { retries: 1 });
      if (res.ok) {
        const data = await res.json();
        cachedData = data;
        cacheTimestamp = Date.now();
        return data;
      }
    } catch {
      // Fallback: individual endpoints will handle their own errors
    } finally {
      pendingFetch = null;
    }
    return null;
  })();

  return pendingFetch;
}

/** Invalidate the batch cache (e.g. after new learning activity) */
export function invalidateDashboardBatchCache(): void {
  cachedData = null;
  cacheTimestamp = 0;
}

/**
 * Hook that returns a specific section from the batch response.
 * Falls back to null if batch endpoint fails (widgets should handle null gracefully).
 */
export function useDashboardBatch<K extends keyof BatchData>(key: K): BatchData[K] | undefined {
  const [data, setData] = useState<BatchData[K] | undefined>(
    cachedData ? cachedData[key] ?? undefined : undefined,
  );

  useEffect(() => {
    let cancelled = false;
    fetchBatch().then((batch) => {
      if (!cancelled && batch) {
        setData(batch[key] ?? undefined);
      }
    });
    return () => { cancelled = true; };
  }, [key]);

  return data;
}